from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langgraph.checkpoint.memory import MemorySaver

from app.state import GraphState
from app.tools import tools
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=openai_api_key
)
memory = MemorySaver()
llm_with_tools = llm.bind_tools(tools=tools)


async def agent_node(state: GraphState):
    result = await llm_with_tools.ainvoke(state["messages"])
    print("result: ", result)
    return {
        "messages": [result]
    }


tool_node = ToolNode(tools=tools)


def get_graph():
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", tool_node)

    graph_builder.set_entry_point("agent")

    graph_builder.add_conditional_edges("agent", tools_condition)
    graph_builder.add_edge("tools", "agent")  # FIXED: was add()

    return graph_builder.compile(checkpointer=memory)