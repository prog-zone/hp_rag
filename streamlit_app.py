import streamlit as st
import requests

# The URL of your FastAPI backend
API_URL = "http://localhost:8000/api/v1/query"

# --- Page Config ---
st.set_page_config(page_title="Hogwarts RAG Oracle", page_icon="⚡", layout="centered")
st.title("⚡ The Hogwarts RAG Oracle")
st.markdown("Ask any question about the Harry Potter universe. The Oracle will search the sacred texts and provide an answer.")

# --- Initialize Chat History ---
# Streamlit reruns the whole script on every interaction, so we store the chat history in "session_state"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # If it's an assistant message, we also want to render the metrics/sources if they exist
        if message["role"] == "assistant" and "metrics" in message:
            st.caption(message["metrics"])
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for source in message["sources"]:
                    st.markdown(f"- **{source['book_title']}** (Page {source['page']}) | *Relevance Score: {source['dense_score']:.2f}*")

# --- Chat Input ---
if prompt := st.chat_input("E.g., What are the ingredients of Polyjuice Potion?"):
    
    # 1. Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the FastAPI Backend
    with st.chat_message("assistant"):
        with st.spinner("Consulting the Restricted Section... this may take up to 30 seconds..."):
            try:
                # Send the POST request to your FastAPI router
                response = requests.post(API_URL, json={"question": prompt})
                response.raise_for_status() # Raise an exception for bad status codes
                
                data = response.json()
                answer = data.get("answer", "I couldn't find an answer.")
                time_taken = data.get("time_taken_seconds", 0)
                chunks = data.get("chunks_used", 0)
                sources = data.get("sources", [])
                
                metrics_text = f"⏱️ Time: {time_taken}s | 🧩 Chunks Analyzed: {chunks}"
                
                # Display the answer
                st.markdown(answer)
                st.caption(metrics_text)
                
                # Display the sources in a dropdown expander
                if sources:
                    with st.expander("📚 View Sources"):
                        for source in sources:
                            st.markdown(f"- **{source['book_title']}** (Page {source['page']}) | *Relevance Score: {source['dense_score']:.2f}*")
                
                # Save the assistant's response to the session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "metrics": metrics_text,
                    "sources": sources
                })

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is your FastAPI server running?")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")