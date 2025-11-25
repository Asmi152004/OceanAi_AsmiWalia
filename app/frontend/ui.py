import streamlit as st
import requests
import json
import os

# Backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

st.title("🤖 Autonomous QA Agent")
st.markdown("Generate Test Cases and Selenium Scripts from Documentation")

# Sidebar for Configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key Input
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.info("Ensure Backend is running on Port 8000")
    if st.button("Clear Knowledge Base"):
        try:
            res = requests.post(f"{API_URL}/clear-kb")
            if res.status_code == 200:
                st.success("KB Cleared!")
        except:
            st.error("Backend not reachable")

# Tabs
tab1, tab2, tab3 = st.tabs(["📂 Knowledge Base", "🧪 Test Case Generation", "📜 Script Generation"])

# --- Tab 1: Knowledge Base ---
with tab1:
    st.header("Upload Project Assets")
    uploaded_files = st.file_uploader("Upload Support Docs & HTML", accept_multiple_files=True)
    
    if st.button("Build Knowledge Base"):
        if uploaded_files:
            files = [('files', (f.name, f.getvalue(), f.type)) for f in uploaded_files]
            with st.spinner("Ingesting documents..."):
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please upload files first.")

# --- Tab 2: Test Case Generation ---
with tab2:
    st.header("Generate Test Cases")
    user_query = st.text_input("Describe the feature or scope (e.g., 'Generate test cases for discount code')", value="Generate all positive and negative test cases for the discount code feature.")
    
    if st.button("Generate Test Cases"):
        with st.spinner("Analyzing Knowledge Base & Generating Cases..."):
            try:
                payload = {"query": user_query}
                response = requests.post(f"{API_URL}/generate-test-cases", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if "test_cases" in data:
                        st.session_state['test_cases'] = data['test_cases']
                        st.success(f"Generated {len(data['test_cases'])} Test Cases")
                    else:
                        st.error("Invalid response format from Agent")
                        st.write(data)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display Test Cases
    if 'test_cases' in st.session_state:
        st.subheader("Generated Test Cases")
        for tc in st.session_state['test_cases']:
            with st.expander(f"{tc.get('id', 'N/A')}: {tc.get('scenario', 'No Scenario')}"):
                st.write(f"**Feature:** {tc.get('feature')}")
                st.write(f"**Expected Result:** {tc.get('expected_result')}")
                st.write(f"**Grounded In:** {tc.get('grounded_in')}")

# --- Tab 3: Script Generation ---
with tab3:
    st.header("Generate Selenium Script")
    
    if 'test_cases' in st.session_state:
        # Select Test Case
        tc_options = {f"{tc.get('id')} - {tc.get('scenario')}": tc for tc in st.session_state['test_cases']}
        selected_option = st.selectbox("Select a Test Case", list(tc_options.keys()))
        
        # We need the HTML content. Ideally, we pick it from the uploaded files or just paste it here for context if needed.
        # For this demo, let's assume the backend has it or we re-upload/paste it.
        # To make it robust, let's allow pasting HTML here if it wasn't in the KB, or just rely on KB.
        # Actually, the prompt says "Retrieve the full content of checkout.html". 
        # Since we uploaded it to KB, we might retrieve it, but RAG chunks it. 
        # Better to have a dedicated "Target HTML" input or just assume it's in the assets folder on the server?
        # The server can read 'assets/checkout.html' if it exists.
        # Let's add a text area for HTML content just in case, pre-filled if possible.
        
        html_input = st.text_area("Target HTML Content (Paste if needed, or Agent will try to find it)", height=200)
        
        if st.button("Generate Script"):
            selected_tc = tc_options[selected_option]
            with st.spinner("Generating Selenium Script..."):
                try:
                    payload = {"test_case": selected_tc, "html_content": html_input}
                    response = requests.post(f"{API_URL}/generate-script", json=payload)
                    if response.status_code == 200:
                        script = response.json().get('script', '')
                        st.code(script, language='python')
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Generate Test Cases in Tab 2 first.")
