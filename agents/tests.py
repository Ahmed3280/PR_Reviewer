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
Limit your response to the TOP 10 most important missing tests only.
Focus on the most critical untested functions first.
Be concise — maximum 2 sentences per issue.

Before flagging anything:
- Check carefully whether a corresponding test already exists in the diff
- Look inside classes for new methods, not just top-level functions
- A function is only missing a test if NO test for it appears anywhere in the diff

Look for:
- New functions or class methods added with no corresponding test_ function
- Critical logic paths with no test coverage
- Edge cases that are clearly unhandled and untested

If you find corresponding tests already in the diff, say 'No test coverage issues found.'
Be specific: mention the exact function name that needs a test and why.
If everything looks tested, say 'No test coverage issues found.'
Do not write any intro sentence. Start directly with: 1. [finding]"""),
        
        HumanMessage(content=f"""Review this diff:\n\n{diff}""")
        
    ]
    response = llm.invoke(messages)
    return response.content