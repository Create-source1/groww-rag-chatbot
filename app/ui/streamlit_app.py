"""Streamlit chat interface for the Groww RAG Chatbot."""
import os
import requests
import streamlit as st

# Page config
st.set_page_config(
    page_title="Groww RAG Chatbot",
    page_icon="📈",
    layout="centered"
)

# API URL
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None


def call_chat_api(query: str) -> dict:
    """Call the chat API endpoint."""
    payload = {
        "query": query,
        "session_id": st.session_state.session_id,
        "history": []
    }
    try:
        response = requests.post(f"{API_URL}/api/chat", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"response": "Cannot connect to the API server. Please check if it's running.", "sources": []}
    except requests.exceptions.Timeout:
        return {"response": "The request timed out. Please try again.", "sources": []}
    except Exception as e:
        return {"response": f"An error occurred: {str(e)}", "sources": []}


def main():
    """Main Streamlit app."""
    st.title("📈 Groww RAG Chatbot")
    st.caption("Answers about HDFC mutual fund schemes — expense ratio, exit load, SIP, lock-in, benchmark and more.")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info(
            "This is a RAG-powered FAQ assistant over official Groww pages for 5 HDFC "
            "mutual fund schemes. It answers factual questions only — no investment advice."
        )

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        # Document management
        st.header("Add Documents")
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "txt", "md", "docx"]
        )
        if uploaded_file and st.button("Ingest Document"):
            with st.spinner("Ingesting..."):
                data = {"title": uploaded_file.name}
                try:
                    resp = requests.post(
                        f"{API_URL}/api/ingest",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                        data=data,
                        timeout=60
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(f"Ingested '{result['title']}' ({result['chunks_ingested']} chunks)")
                    else:
                        st.error(f"Ingestion failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = call_chat_api(prompt)

            st.markdown(result["response"])

            # Display sources (official page URLs)
            if result.get("sources"):
                with st.expander("📚 Sources"):
                    for source in result["sources"]:
                        st.write(f"**{source['document_title']}** — {source['source']}")

        # Save to session
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"]
        })
        if result.get("session_id"):
            st.session_state.session_id = result["session_id"]


if __name__ == "__main__":
    main()
