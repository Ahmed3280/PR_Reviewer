# PR Reviewer — Multi-Agent Code Review Tool

A multi-agent system built with LangGraph that automatically reviews 
GitHub pull requests for security vulnerabilities, style issues, 
and missing tests.

## Architecture

- **Security Agent** — finds vulnerabilities, injections, hardcoded secrets
- **Style Agent** — finds readability and maintainability issues  
- **Test Agent** — finds missing or insufficient tests
- **Manager Graph** — orchestrates agents via LangGraph, synthesizes final verdict

## Setup

1. Clone the repo
2. Create a virtual environment
```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
```
3. Install dependencies
```bash
   pip install -r requirements.txt
```
4. Create a `.env` file