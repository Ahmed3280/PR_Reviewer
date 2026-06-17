import difflib
import re
from typing import Literal

BugType = Literal[
    "sql_injection",
    "hardcoded_secret",
    "missing_input_validation",
    "bad_variable_name",
    "missing_docstring",
    "missing_test",
]


def _make_diff(filename: str, clean: str, buggy: str) -> str:
    clean_lines = clean.splitlines(keepends=True)
    buggy_lines = buggy.splitlines(keepends=True)
    diff = difflib.unified_diff(
        clean_lines,
        buggy_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff)


def _bug_line(diff: str) -> int:
    """Return the line number of the first + (added) line in the diff."""
    for i, line in enumerate(diff.splitlines(), 1):
        if line.startswith("+") and not line.startswith("+++"):
            return i
    return 1


def inject_sql_injection(snippet: str) -> dict:
    # Extract the parameter variable name from cursor.execute(query, (varname,))
    m = re.search(r'cursor\.execute\(query,\s*\((\w+),\)\)', snippet)
    if not m:
        raise ValueError("inject_sql_injection: no parameterized execute found in snippet")
    varname = m.group(1)
    # Remove the safe query variable and replace execute with string concatenation
    buggy = re.sub(
        r'    query = "SELECT \* FROM \w+ WHERE \w+ = \?"\n',
        '    # query built with string concatenation\n',
        snippet,
    )
    buggy = re.sub(
        r'    cursor\.execute\(query,\s*\(\w+,\)\)',
        f'    cursor.execute("SELECT * FROM t WHERE col = \'" + {varname} + "\'")',
        buggy,
    )
    diff = _make_diff("db.py", snippet, buggy)
    return {
        "diff": diff,
        "bug_line": _bug_line(diff),
        "bug_type": "sql_injection",
        "description": "SQL query built with string concatenation instead of parameterized query",
    }


def inject_hardcoded_secret(snippet: str) -> dict:
    clean = snippet
    buggy = snippet.replace(
        'api_key = os.environ.get("API_KEY")',
        'api_key = "sk-prod-abc123XYZ987secretkey"',
    )
    diff = _make_diff("config.py", clean, buggy)
    return {
        "diff": diff,
        "bug_line": _bug_line(diff),
        "bug_type": "hardcoded_secret",
        "description": "API key hardcoded as a plaintext string literal instead of read from environment",
    }


def inject_missing_input_validation(snippet: str) -> dict:
    clean = snippet
    buggy = snippet.replace(
        '    if not user_input or len(user_input) > 200:\n        raise ValueError("Invalid input")\n    ',
        '    ',
    )
    diff = _make_diff("handler.py", clean, buggy)
    return {
        "diff": diff,
        "bug_line": _bug_line(diff),
        "bug_type": "missing_input_validation",
        "description": "User input used directly without length or emptiness validation",
    }


def inject_bad_variable_name(snippet: str) -> dict:
    clean = snippet
    buggy = (
        snippet
        .replace("total_price", "x")
        .replace("item_count", "a")
        .replace("discount_rate", "b")
    )
    diff = _make_diff("pricing.py", clean, buggy)
    return {
        "diff": diff,
        "bug_line": _bug_line(diff),
        "bug_type": "bad_variable_name",
        "description": "Meaningful variable names replaced with single-letter identifiers",
    }


def inject_missing_docstring(snippet: str) -> dict:
    clean = snippet
    buggy = snippet.replace(
        '    """Calculate the total price after applying discount."""\n    ',
        '    ',
    )
    diff = _make_diff("pricing.py", clean, buggy)
    return {
        "diff": diff,
        "bug_line": _bug_line(diff),
        "bug_type": "missing_docstring",
        "description": "Function is missing a docstring explaining its purpose",
    }


def inject_missing_test(snippet: str) -> dict:
    clean = snippet
    new_function = (
        "\n\ndef process_refund(order_id: int, amount: float) -> bool:\n"
        "    if amount <= 0:\n"
        "        return False\n"
        "    db.execute('UPDATE orders SET refunded=1 WHERE id=?', (order_id,))\n"
        "    return True\n"
    )
    buggy = snippet + new_function
    diff = _make_diff("orders.py", clean, buggy)
    return {
        "diff": diff,
        "bug_line": _bug_line(diff),
        "bug_type": "missing_test",
        "description": "New function process_refund added with no corresponding test",
    }


_INJECTORS = {
    "sql_injection": inject_sql_injection,
    "hardcoded_secret": inject_hardcoded_secret,
    "missing_input_validation": inject_missing_input_validation,
    "bad_variable_name": inject_bad_variable_name,
    "missing_docstring": inject_missing_docstring,
    "missing_test": inject_missing_test,
}


def inject_bug(snippet: str, bug_type: BugType) -> dict:
    return _INJECTORS[bug_type](snippet)
