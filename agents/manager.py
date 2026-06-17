from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.security import run_security_review
from agents.style import run_style_review
from agents.tests import run_test_review

# Shared State - Dictionary flows through the Graph.
class ReviewState(TypedDict):
    diff : str
    security_findings : str
    style_findings : str
    test_findings : str
    final_verdict : str
    
# Each node in the graph is a function that takes in the shared state and returns a new state.
def security_node(state: ReviewState) -> ReviewState:
    print("Running security review...")
    result = run_security_review(state["diff"])
    return {"security_findings": result}

def style_node(state: ReviewState) -> ReviewState:
    print("Running style review...")
    result = run_style_review(state["diff"])
    return {"style_findings": result}

def test_node(state: ReviewState) -> ReviewState:
    print("Running test review...")
    result = run_test_review(state["diff"])
    return {"test_findings": result}

def verdict_node(state: ReviewState) -> ReviewState:
    print("Compiling final verdict...")
    
    combined = f"""
    Security Findings:
    {state["security_findings"]}
    
    Style Findings:
    {state["style_findings"]}
    
    Test Findings:
    {state["test_findings"]}
    """
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage 
    from dotenv import load_dotenv
    import os

    load_dotenv()

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                google_api_key=os.getenv("GOOGLE_API_KEY")
                             )

    messages = [
        SystemMessage(content="""You are a senior engineer giving a final PR verdict.
        You will receive findings from three reviewers: security, style, and tests.
        Based on all findings, give:
        1. A verdict: APPROVE, REQUEST CHANGES, or COMMENT
        2. A short summary of the most critical issues
        Be concise and decisive."""),
        HumanMessage(content=combined)
        ]

    response = llm.invoke(messages)
    return {"final_verdict": response.content}

# Build The Graph
def build_graph():
    graph = StateGraph(ReviewState)
    
    # Add Nodes
    graph.add_node("security", security_node)
    graph.add_node("style", style_node)
    graph.add_node("tests", test_node)
    graph.add_node("verdict", verdict_node)
    
    #Set the entry point
    graph.set_entry_point("security")
    
    # Connect nodes in sequence
    graph.add_edge("security", "style")
    graph.add_edge("style", "tests")
    graph.add_edge("tests", "verdict")
    graph.add_edge("verdict", END)
    
    return graph.compile()