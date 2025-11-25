import streamlit as st
import os
from typing import List, Dict
import json

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# Document parsing
from bs4 import BeautifulSoup

# Set page config
st.set_page_config(page_title="Autonomous QA Agent", layout="wide", page_icon="🤖")

# Initialize session state
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'html_content' not in st.session_state:
    st.session_state.html_content = ""

# Document parsing functions
def parse_document(filename: str, content: bytes) -> str:
    if filename.endswith('.md') or filename.endswith('.txt'):
        return content.decode('utf-8')
    elif filename.endswith('.json'):
        data = json.loads(content.decode('utf-8'))
        return json.dumps(data, indent=2)
    elif filename.endswith('.html'):
        return content.decode('utf-8')
    else:
        return content.decode('utf-8', errors='ignore')

# RAG functions
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_documents(documents: List[Dict[str, str]], embeddings):
    docs = []
    for doc in documents:
        docs.append(Document(page_content=doc['content'], metadata={"source": doc['source']}))
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(docs)
    
    if chunks:
        vector_db = Chroma.from_documents(
            chunks, embeddings, persist_directory="./chroma_db"
        )
        return vector_db, len(chunks)
    return None, 0

def retrieve_context(vector_db, query: str, k: int = 5):
    if not vector_db:
        return []
    return vector_db.similarity_search(query, k=k)

# LLM functions
def initialize_llm(api_key: str):
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        return ChatOpenAI(model="gpt-4o", temperature=0)
    return None

def generate_test_cases(llm, context: str, query: str):
    if not llm:
        return {"error": "LLM not configured. Please enter your OpenAI API key."}
    
    prompt = ChatPromptTemplate.from_template("""
    You are an expert QA Automation Engineer.
    Based on the following context (Project Documentation and HTML structure), generate a comprehensive list of test cases for the requested feature.
    
    Context:
    {context}
    
    User Request: {query}
    
    Output Format:
    Provide the response as a JSON object with a key "test_cases" containing a list of objects.
    Each object should have:
    - "id": "TC-XXX"
    - "feature": "Feature Name"
    - "scenario": "Description of the test scenario"
    - "expected_result": "Expected outcome"
    - "grounded_in": "Source document filename"
    
    Ensure NO hallucinations. Only use features described in the context.
    """)
    
    chain = prompt | llm | JsonOutputParser()
    try:
        result = chain.invoke({"context": context, "query": query})
        return result
    except Exception as e:
        return {"error": str(e)}

def generate_selenium_script(llm, test_case: dict, html_content: str, context: str):
    if not llm:
        return "Error: LLM not configured. Please enter your OpenAI API key."
    
    prompt = ChatPromptTemplate.from_template("""
    You are an expert Python Selenium Automation Engineer.
    Generate a complete, runnable Python Selenium script for the following test case.
    
    Test Case:
    {test_case}
    
    HTML Structure (Target Page):
    {html_content}
    
    Additional Context (Rules/Specs):
    {context}
    
    Requirements:
    1. Use 'webdriver.Chrome()' (assume chromedriver is in path or managed by webdriver-manager).
    2. Use explicit waits (WebDriverWait) where appropriate.
    3. Use precise selectors based on the provided HTML (ID, CSS, XPath).
    4. Include assertions to verify the Expected Result.
    5. Return ONLY the Python code in a clean format.
    """)
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"test_case": test_case, "html_content": html_content, "context": context})

# UI
st.title("🤖 Autonomous QA Agent")
st.markdown("Generate Test Cases and Selenium Scripts from Documentation")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
    
    if api_key and st.session_state.llm is None:
        st.session_state.llm = initialize_llm(api_key)
        st.success("✅ LLM Initialized")
    
    if st.session_state.embeddings is None:
        with st.spinner("Loading embeddings model..."):
            st.session_state.embeddings = get_embeddings()
        st.success("✅ Embeddings Loaded")
    
    st.divider()
    st.markdown("### 📊 Status")
    if st.session_state.vector_db:
        st.success("✅ Knowledge Base Ready")
    else:
        st.warning("⚠️ No Knowledge Base")
    
    if st.button("🗑️ Clear Knowledge Base"):
        st.session_state.vector_db = None
        st.session_state.test_cases = None
        st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["📂 Knowledge Base", "🧪 Test Case Generation", "📜 Script Generation"])

# Tab 1: Knowledge Base
with tab1:
    st.header("Upload Project Assets")
    st.markdown("Upload your project documentation and HTML files to build the knowledge base.")
    
    uploaded_files = st.file_uploader(
        "Upload Support Docs & HTML", 
        accept_multiple_files=True,
        help="Supported formats: .md, .txt, .json, .html"
    )
    
    if st.button("🔨 Build Knowledge Base", type="primary"):
        if uploaded_files:
            documents = []
            for file in uploaded_files:
                content = file.read()
                text = parse_document(file.name, content)
                documents.append({"content": text, "source": file.name})
                
                # Store HTML content if it's an HTML file
                if file.name.endswith('.html'):
                    st.session_state.html_content = text
            
            with st.spinner("Ingesting documents and building vector database..."):
                vector_db, count = ingest_documents(documents, st.session_state.embeddings)
                st.session_state.vector_db = vector_db
            
            if vector_db:
                st.success(f"✅ Successfully ingested {count} chunks from {len(uploaded_files)} files!")
                st.balloons()
            else:
                st.error("❌ Failed to build knowledge base")
        else:
            st.warning("⚠️ Please upload files first")

# Tab 2: Test Case Generation
with tab2:
    st.header("Generate Test Cases")
    
    if not st.session_state.vector_db:
        st.warning("⚠️ Please build the Knowledge Base first (Tab 1)")
    else:
        user_query = st.text_area(
            "Describe the feature or test scope",
            value="Generate all positive and negative test cases for the discount code feature.",
            height=100
        )
        
        if st.button("🧪 Generate Test Cases", type="primary"):
            if not st.session_state.llm:
                st.error("❌ Please enter your OpenAI API key in the sidebar")
            else:
                with st.spinner("Analyzing Knowledge Base & Generating Test Cases..."):
                    # Retrieve context
                    context_docs = retrieve_context(st.session_state.vector_db, user_query, k=5)
                    context_text = "\n\n".join([
                        f"Source: {d.metadata['source']}\nContent: {d.page_content}" 
                        for d in context_docs
                    ])
                    
                    # Generate test cases
                    result = generate_test_cases(st.session_state.llm, context_text, user_query)
                    
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    elif "test_cases" in result:
                        st.session_state.test_cases = result['test_cases']
                        st.success(f"✅ Generated {len(result['test_cases'])} Test Cases")
                    else:
                        st.error("❌ Invalid response format")
                        st.json(result)
        
        # Display test cases
        if 'test_cases' in st.session_state and st.session_state.test_cases:
            st.divider()
            st.subheader("📋 Generated Test Cases")
            
            for tc in st.session_state.test_cases:
                with st.expander(f"**{tc.get('id', 'N/A')}**: {tc.get('scenario', 'No Scenario')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Feature:** {tc.get('feature')}")
                        st.markdown(f"**Expected Result:** {tc.get('expected_result')}")
                    with col2:
                        st.markdown(f"**Grounded In:** {tc.get('grounded_in')}")

# Tab 3: Script Generation
with tab3:
    st.header("Generate Selenium Script")
    
    if 'test_cases' not in st.session_state or not st.session_state.test_cases:
        st.info("ℹ️ Generate Test Cases in Tab 2 first")
    else:
        # Select test case
        tc_options = {
            f"{tc.get('id')} - {tc.get('scenario')}": tc 
            for tc in st.session_state.test_cases
        }
        selected_option = st.selectbox("Select a Test Case", list(tc_options.keys()))
        
        # HTML content input
        html_input = st.text_area(
            "Target HTML Content (Optional - will use uploaded HTML if available)",
            value=st.session_state.html_content,
            height=200,
            help="Paste HTML content or leave as-is if you uploaded an HTML file"
        )
        
        if st.button("📜 Generate Selenium Script", type="primary"):
            if not st.session_state.llm:
                st.error("❌ Please enter your OpenAI API key in the sidebar")
            else:
                selected_tc = tc_options[selected_option]
                
                with st.spinner("Generating Selenium Script..."):
                    # Retrieve context
                    context_docs = retrieve_context(
                        st.session_state.vector_db, 
                        selected_tc.get('feature', ''), 
                        k=3
                    )
                    context_text = "\n\n".join([
                        f"Source: {d.metadata['source']}\nContent: {d.page_content}" 
                        for d in context_docs
                    ])
                    
                    # Generate script
                    script = generate_selenium_script(
                        st.session_state.llm,
                        selected_tc,
                        html_input,
                        context_text
                    )
                    
                    st.success("✅ Script Generated!")
                    st.code(script, language='python')
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Script",
                        data=script,
                        file_name=f"{selected_tc.get('id', 'test')}_script.py",
                        mime="text/plain"
                    )
