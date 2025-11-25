import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from .schemas import TestPlan

# Placeholder for LLM initialization
# In a real scenario, we might want to support Ollama or others dynamically.
# For this assignment, we'll default to OpenAI if key exists, else warn.

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found. LLM features will fail unless configured.")
            # Fallback or dummy could be implemented here
            self.llm = None
        else:
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def generate_test_cases(self, context: str, query: str) -> str:
        if not self.llm:
            return "Error: LLM not configured."

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
        
        chain = prompt | self.llm | JsonOutputParser()
        try:
            result = chain.invoke({"context": context, "query": query})
            return result
        except Exception as e:
            return {"error": str(e)}

    def generate_selenium_script(self, test_case: dict, html_content: str, context: str) -> str:
        if not self.llm:
            return "Error: LLM not configured."

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
        5. Return ONLY the Python code, no markdown formatting if possible, or inside a single code block.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"test_case": test_case, "html_content": html_content, "context": context})
