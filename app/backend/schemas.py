from pydantic import BaseModel
from typing import List, Optional

class TestCase(BaseModel):
    id: str
    feature: str
    scenario: str
    expected_result: str
    grounded_in: str

class TestPlan(BaseModel):
    test_cases: List[TestCase]

class ScriptRequest(BaseModel):
    test_case: TestCase
    html_content: Optional[str] = None # Optional, can be retrieved from KB if indexed
