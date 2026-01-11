import json
import time
import streamlit as st
import httpx

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="AI Chat", layout="centered")
st.title("AI Chat with streaming")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input + Submit button
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:", key="input_box", placeholder="Ask any question")
    submitted = st.form_submit_button("Submit")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    search_urls = []

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        # Show simple typing animation before real stream
        for i in range(3):
            placeholder.markdown("Hold on" + "." * (i + 1))
            time.sleep(0.4)

        def stream_from_api():
            try:
                payload = {
                    "query": user_input,
                    "thread_id": st.session_state.thread_id or "new"
                }
                
                with httpx.stream("POST", API_URL, json=payload, timeout=60.0) as response:
                    for chunk in response.iter_text():
                        if not chunk.strip():
                            continue
                        try:
                            clean_chunk = chunk.replace("data: ", "").strip()
                            if not clean_chunk:
                                continue
                                
                            data = json.loads(clean_chunk)
                            
                            if data.get("type") == "checkpoint":
                                st.session_state.thread_id = data.get("checkpoint_id")
                            elif data.get("type") == "content":
                                yield data.get("content", "")
                            elif data.get("type") == "search_results":
                                search_urls.extend(data.get("urls", []))
                            elif data.get("type") == "error":
                                st.error(f"Error: {data.get('message')}")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, chunk: {chunk}")
                            continue
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                yield "Sorry, there was an error connecting to the server."

        full_response = placeholder.write_stream(stream_from_api())

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # THIS ENTIRE SECTION MUST BE INDENTED (inside the if submitted block)
    if search_urls:
        st.markdown("### 🔗 Related Research Links")

        st.markdown("""
            <style>
                .url-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                    margin-top: 20px;
                    margin-bottom: 20px;
                }
                .url-box {
                    border: 1px solid #ddd;
                    padding: 20px;
                    border-radius: 10px;
                    min-height: 120px;
                    box-sizing: border-box;
                    background-color: #f9f9f9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    transition: all 0.3s ease;
                }
                .url-box:hover {
                    background-color: #f0f0f0;
                    border-color: #0066cc;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                .url-box a {
                    color: #0066cc;
                    text-decoration: none;
                    word-break: break-word;
                    font-size: 14px;
                    line-height: 1.4;
                }
                .url-box a:hover {
                    text-decoration: underline;
                }
            </style>        
        """, unsafe_allow_html=True)

        box_html = '<div class="url-grid">'
        for url in search_urls[:4]:
            box_html += f'<div class="url-box"><a href="{url}" target="_blank">{url}</a></div>'
        box_html += '</div>'

        st.markdown(box_html, unsafe_allow_html=True)

# Add clear conversation button
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state.messages = []
    st.session_state.thread_id = None
    st.rerun()