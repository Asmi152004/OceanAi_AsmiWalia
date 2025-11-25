# Autonomous QA Agent - Streamlit Cloud Deployment

An intelligent agent that builds a "testing brain" from project documentation and HTML to generate test cases and Selenium scripts.

🔗 **Live Demo**: [Deploy on Streamlit Cloud](https://share.streamlit.io/)

## Features
- **Knowledge Base Ingestion**: Upload and process MD, TXT, JSON, and HTML files
- **Test Case Generation**: Uses RAG + LLM to create grounded test cases
- **Selenium Script Generation**: Converts test cases into executable Python Selenium scripts

## Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run the App**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Enter your OpenAI API Key** in the sidebar

4. **Upload Files** from the `assets/` folder and start generating test cases!

## Deployment on Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Sign in with GitHub
4. Click "New app"
5. Select this repository
6. Set main file path to: `streamlit_app.py`
7. Add your OpenAI API key in "Secrets" (Advanced settings):
   ```toml
   OPENAI_API_KEY = "your-key-here"
   ```
8. Click "Deploy"!

## Project Structure
- `streamlit_app.py`: Main Streamlit application
- `assets/`: Sample project files (checkout.html, specs, etc.)
- `requirements_streamlit.txt`: Python dependencies

## Usage

### 1. Build Knowledge Base
- Upload your project documentation and HTML files
- Click "Build Knowledge Base"

### 2. Generate Test Cases
- Enter a query describing what you want to test
- Click "Generate Test Cases"
- Review the generated test cases

### 3. Generate Selenium Scripts
- Select a test case from the dropdown
- Click "Generate Selenium Script"
- Download and run the script

## Example Files Included
- `checkout.html`: Sample e-commerce checkout page
- `product_specs.md`: Product specifications
- `ui_ux_guide.txt`: UI/UX guidelines
- `api_endpoints.json`: API documentation

## Tech Stack
- **Frontend**: Streamlit
- **RAG**: ChromaDB + HuggingFace Embeddings
- **LLM**: OpenAI GPT-4
- **Vector Search**: LangChain

## License
MIT
