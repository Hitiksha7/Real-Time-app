from typing import Optional
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessageChunk
from pydantic import BaseModel, Field
from app.graph import get_graph

# Create Graph Object
graph = get_graph()

# Create FastAPI Object
app = FastAPI()

# Add CORS middleware with frontend requirements
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"]
)


def serialise_ai_message_chunk(chunk):
    """Serialize AI message chunk to string content."""
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly "
            f"formatted for serialisation"
        )


async def generate_chat_responses(
    message: str,
    checkpoint_id: Optional[str] = None
):
    """
    Generate streaming chat responses with tool calling support.

    Args:
        message: User's input message
        checkpoint_id: Thread ID for conversation memory.

    Yields:
        Server-sent events with chat responses and tool results
    """
    try:
        is_new_conversation = (
            checkpoint_id is None or checkpoint_id == "new"
        )

        if is_new_conversation:
            new_checkpoint_id = str(uuid4())

            config = {
                "configurable": {
                    "thread_id": new_checkpoint_id
                }
            }

            events = graph.astream_events(
                {"messages": [HumanMessage(content=message)]},
                version="v2",
                config=config
            )

            checkpoint_data = {
                "type": "checkpoint",
                "checkpoint_id": new_checkpoint_id
            }
            yield f"data: {json.dumps(checkpoint_data)}\n\n"
        else:
            config = {
                "configurable": {
                    "thread_id": checkpoint_id
                }
            }

            events = graph.astream_events(
                {"messages": [HumanMessage(content=message)]},
                version="v2",
                config=config
            )

        async for event in events:
            event_type = event["event"]

            if event_type == "on_chat_model_stream":
                chunk_content = serialise_ai_message_chunk(
                    event["data"]["chunk"]
                )

                # Use json.dumps to handle escaping automatically
                content_data = {
                    "type": "content",
                    "content": chunk_content
                }
                yield f"data: {json.dumps(content_data)}\n\n"

            elif event_type == "on_chat_model_end":
                output = event["data"]["output"]
                tool_calls = (
                    output.tool_calls
                    if hasattr(output, "tool_calls")
                    else []
                )
                search_calls = [
                    call for call in tool_calls
                    if call["name"] == "tavily_search"
                ]

                if search_calls:
                    search_query = search_calls[0]["args"].get("query", "")

                    search_data = {
                        "type": "search_start",
                        "query": search_query
                    }
                    yield f"data: {json.dumps(search_data)}\n\n"

            elif (
                event_type == "on_tool_end" and 
                event["name"] == "tavily_search"
            ):
                output = event["data"]["output"]

                try:
                    if hasattr(output, 'content'):
                        content = output.content

                        if isinstance(content, str):
                            results = json.loads(content)
                        else:
                            results = content

                        urls = []
                        if isinstance(results, list):
                            for item in results:
                                if isinstance(item, dict) and "url" in item:
                                    urls.append(item["url"])
                        elif (
                            isinstance(results, dict) and 
                            "results" in results
                        ):
                            for item in results["results"]:
                                if isinstance(item, dict) and "url" in item:
                                    urls.append(item["url"])

                        if urls:
                            results_data = {
                                "type": "search_results",
                                "urls": urls
                            }
                            yield f"data: {json.dumps(results_data)}\n\n"
                except Exception as e:
                    print(f"Error processing tool output: {e}")

        end_data = {"type": "end"}
        yield f"data: {json.dumps(end_data)}\n\n"

    except Exception as e:
        print(f"ERROR in generate_chat_responses: {e}")
        import traceback
        traceback.print_exc()
        error_data = {
            "type": "error",
            "message": "An error occurred"
        }
        yield f"data: {json.dumps(error_data)}\n\n"


class InputData(BaseModel):
    """Input schema for chat endpoint."""
    query: str
    thread_id: str = Field(default="001")


@app.post("/chat")
async def chat_stream(input: InputData):
    """
    Stream chat responses with real-time updates.
    Args:
        input: User query and thread ID
    Returns:
        StreamingResponse with server-sent events
    """
    return StreamingResponse(
        generate_chat_responses( 
            message=input.query,
            checkpoint_id=input.thread_id
        ),
        media_type="text/event-stream"
    )