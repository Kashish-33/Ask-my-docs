import streamlit as st
import requests

# configuration
#API_URL = "http://0.0.0.0:8000"
API_URL = "http://localhost:8000"

# Page- setup
st.set_page_config(
    page_title="Ask My Docs",
    page_icon="📄",
    layout="centered"
)

st.markdown("""
<style>
    /* Overall background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Title styling */
    h1 {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
    }

    /* Caption/subtitle */
    .stCaption {
        color: #a0a0c0 !important;
        font-size: 1rem !important;
    }

    /* Chat input box */
    .stChatInput textarea {
        background-color: #1e1e3a !important;
        border: 1px solid #7b2ff7 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }

    /* User message bubble */
    [data-testid="stChatMessageContent"] {
        background-color: #1e1e3a !important;
        border-radius: 12px !important;
        border: 1px solid #2a2a4a !important;
        color: #e0e0ff !important;
    }

    /* Expander (source chunks) */
    .streamlit-expanderHeader {
        background-color: #1a1a2e !important;
        color: #00d2ff !important;
        border-radius: 8px !important;
    }

    /* Spinner text */
    .stSpinner {
        color: #7b2ff7 !important;
    }

    /* Divider color */
    hr {
        border-color: #2a2a4a !important;
    }
</style>
""", unsafe_allow_html=True)

# main heading
st.title("📄 Ask My Docs")
st.caption("Upload a PDF and ask questions about it!")


with st.sidebar:
    st.header("📂 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        if st.button(" Process PDF"):
            with st.spinner("Processing PDF..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name,
                                   uploaded_file.getvalue(),
                                   "application/pdf")}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success(data["message"])
                    st.info(f" Chunks created: {data['chunks']}")
                    st.session_state.chat_history = []
                else:
                    st.error("Upload failed!")

    st.divider()
    st.caption("Powered by RAG + Groq ")


# session state - chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# input section
question = st.chat_input("Ask a question about your document...")

if question:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": data["answer"],
                    "chunks": data["top_chunks"],
                    "confidence": data.get("confidence_score", "N/A"),
                    "retries": data.get("retries_used", 0)
                })

            else:
                st.error(f"API Error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("FastAPI server is not working! 'Run uvicorn main:app --reload")
        except requests.exceptions.Timeout:
            st.error("Request timeout- Groq is slow, Retry.")        

# Display chat History
for chat in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.write(chat["answer"])

            confidence = chat.get("confidence", "N/A")
            retries = chat.get("retries", 0)

            if confidence != "N/A" and confidence >= 4:
                st.caption(f"✅ Confidence: {confidence}/5" + (f" · Retried {retries}x" if retries > 0 else ""))
            elif confidence != "N/A":
                st.caption(f"⚠️ Confidence: {confidence}/5" + (f" · Retried {retries}x" if retries > 0 else ""))

                # Top chunks- collapsible section
        with st.expander("📚 View Source Chunks"):
                for i, chunk in enumerate(chat["chunks"]):
                    st.markdown(f"**chunk {i+1}:**")
                    st.caption(chunk)
                    st.divider()
