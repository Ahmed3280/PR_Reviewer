from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

def run_style_review(diff: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                 google_api_key=os.getenv("GOOGLE_API_KEY")
                                 )
    
    messages = [
        SystemMessage(content="""You are a code style reviewer.
        Analyze the given code diff for style and readability issues only.
        Look for: inconsistent naming conventions, missing docstrings, functions that are too long,
        unclear logic, code that is hard to read.
        Do NOT flag security vulnerabilities — only flag readability and style issues.
        Be specific: mention the exact line that has the issue.
        If nothing is wrong, say 'No style issues found.'
                      """),
        HumanMessage(content=f"""Review this diff:\n\n{diff}""")
    ]
    response = llm.invoke(messages)
    return response.content