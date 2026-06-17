import re

BUG_KEYWORDS: dict[str, list[str]] = {
    "sql_injection": [
        "injection", "sql", "concatenat", "parameteriz", "string concat",
        "unsanitized", "user-controlled", "unsafe query",
    ],
    "hardcoded_secret": [
        "hardcoded", "hard-coded", "hard coded", "secret", "password",
        "api_key", "api key", "credential", "plaintext", "plain text",
        "sensitive", "exposed",
    ],
    "missing_input_validation": [
        "validat", "sanitiz", "unsafe input", "unvalidated", "user input",
        "input check", "no check", "without check",
    ],
    "bad_variable_name": [
        "variable name", "naming", "single letter", "single-letter",
        "descriptive", "meaningful", "unclear", "poor name", "rename",
        "readability",
    ],
    "missing_docstring": [
        "docstring", "documentation", "undocumented", "missing doc",
        "no doc", "comment", "describe",
    ],
    "missing_test": [
        "test", "coverage", "untested", "missing test", "no test",
        "test case", "unit test",
    ],
    # clean diffs have no specific bug type — use an empty list
    "clean": [],
}

_AGENT_CLEAN_PHRASES = {
    "security": "no security issues found",
    "style": "no style issues found",
    "tests": "no test coverage issues found",
}


def _agent_said_clean(response_lower: str, expected_agent: str) -> bool:
    phrase = _AGENT_CLEAN_PHRASES.get(expected_agent, "")
    return phrase in response_lower


def _has_keywords(response_lower: str, bug_type: str) -> bool:
    count = sum(1 for kw in BUG_KEYWORDS.get(bug_type, []) if kw in response_lower)
    return count >= 2


def _mentions_line_number(response_lower: str, bug_line: int) -> bool:
    if bug_line < 1:
        return False
    # Match "line 5", "line: 5", "line5", "#5"
    patterns = [
        rf"\bline\s*:?\s*{bug_line}\b",
        rf"#{bug_line}\b",
    ]
    return any(re.search(p, response_lower) for p in patterns)


def score(agent_response: str, test_case: dict) -> dict:
    response_lower = agent_response.lower()
    expected_agent = test_case["expected_agent"]
    bug_type = test_case["bug_type"]
    bug_line = test_case["bug_line"]
    should_find = test_case["should_find"]

    said_clean = _agent_said_clean(response_lower, expected_agent)
    has_kw = _has_keywords(response_lower, bug_type)
    mentions_line = _mentions_line_number(response_lower, bug_line)

    flagged = not said_clean and (has_kw or mentions_line)

    if should_find:
        caught = flagged
        false_positive = False
    else:
        caught = False
        false_positive = flagged

    return {
        "caught": caught,
        "false_positive": false_positive,
        "agent_response": agent_response,
    }
