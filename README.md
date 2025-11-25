# Autonomous QA Agent

An intelligent agent that builds a "testing brain" from project documentation and HTML to generate test cases and Selenium scripts.

## Features
- **Knowledge Base Ingestion**: Uploads and processes MD, TXT, JSON, and HTML.
- **Test Case Generation**: Uses RAG + LLM to create grounded test cases.
- **Selenium Script Generation**: Converts test cases into executable Python Selenium scripts.

## Setup

1. **Prerequisites**: Python 3.9+
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   Create a `.env` file if using OpenAI or other API keys.
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Usage

### Running the Application
The application consists of a FastAPI backend and a Streamlit frontend.

1. **Start the Backend**:
   ```bash
   uvicorn app.backend.main:app --reload --port 8000
   ```

2. **Start the Frontend**:
   ```bash
   streamlit run app/frontend/ui.py
   ```

3. **Workflow**:
   - Go to the Streamlit UI (http://localhost:8501).
   - **Upload**: Upload `assets/checkout.html` and support docs from `assets/`.
   - **Build KB**: Click the button to ingest data.
   - **Agent**: Ask for test cases (e.g., "Generate test cases for shipping").
   - **Script**: Select a case and generate the Selenium script.

## Project Structure
- `app/backend`: FastAPI server & Logic.
- `app/frontend`: Streamlit UI.
- `assets`: Sample project files.
