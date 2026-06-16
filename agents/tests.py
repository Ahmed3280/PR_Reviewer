from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

def run_test_review(diff: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                 google_api_key=os.getenv("GOOGLE_API_KEY")
                                 )
    
    messages = [
        SystemMessage(content="""You are a test coverage reviewer.
        Analyze the given code diff for missing tests only.
        Look for: new functions with no corresponding test, edge cases not covered,
        critical logic that has no test at all.
        Be specific: mention exactly what needs a test and why.
        If everything looks tested, say 'No test coverage issues found.'"""),
        
        HumanMessage(content=f"""Review this diff:\n\n{diff}""")
        
    ]
    response = llm.invoke(messages)
    return response.content