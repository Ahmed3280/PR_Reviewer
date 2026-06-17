from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
def run_security_review(diff: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                 google_api_key=os.getenv("GOOGLE_API_KEY")
                                 )
    
    messages = [
        SystemMessage(content="""You are a security code reviewer.
        Limit your response to the TOP 10 most critical security issues only, 
        ordered by severity (critical first). Be concise — maximum 2 sentences per issue.
        Analyze the given code diff for security vulnerabilities only.
        Look for: SQL injection, hardcoded secrets, unsafe inputs, exposed credentials.
        Be specific: mention the exact line that has the issue.
        If nothing is wrong, say 'No security issues found.
        Do not write any intro sentence. Start directly with: 1. [finding]
                      """),
        HumanMessage(content=f"""Review this diff:\n\n{diff}""")
    ]
    response = llm.invoke(messages)
    return response.content