from evals.inject import inject_bug

# ---------------------------------------------------------------------------
# Clean base snippets — one per bug family
# ---------------------------------------------------------------------------

_SQL_SNIPPET_1 = """\
import sqlite3

def get_user(username: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchone()
"""

_SQL_SNIPPET_2 = """\
import sqlite3

def get_order(order_id: int):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM orders WHERE id = ?"
    cursor.execute(query, (order_id,))
    return cursor.fetchone()
"""

_SQL_SNIPPET_3 = """\
import sqlite3

def search_products(category: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE category = ?"
    cursor.execute(query, (category,))
    return cursor.fetchall()
"""

_SECRET_SNIPPET_1 = """\
import os

def get_client():
    api_key = os.environ.get("API_KEY")
    return ApiClient(api_key)
"""

_SECRET_SNIPPET_2 = """\
import os

def connect_db():
    api_key = os.environ.get("API_KEY")
    host = os.environ.get("DB_HOST", "localhost")
    return Database(host=host, key=api_key)
"""

_SECRET_SNIPPET_3 = """\
import os

def send_email(to: str, subject: str, body: str):
    api_key = os.environ.get("API_KEY")
    mailer = MailClient(api_key)
    mailer.send(to=to, subject=subject, body=body)
"""

_VALIDATION_SNIPPET_1 = """\
def handle_comment(user_input: str) -> str:
    if not user_input or len(user_input) > 200:
        raise ValueError("Invalid input")
    return db.save_comment(user_input)
"""

_VALIDATION_SNIPPET_2 = """\
def handle_search(user_input: str) -> list:
    if not user_input or len(user_input) > 200:
        raise ValueError("Invalid input")
    return db.search(user_input)
"""

_BAD_NAME_SNIPPET_1 = """\
def calculate_total(total_price: float, item_count: int, discount_rate: float) -> float:
    total_price = total_price * item_count
    total_price = total_price * (1 - discount_rate)
    return total_price
"""

_BAD_NAME_SNIPPET_2 = """\
def apply_discount(total_price: float, item_count: int, discount_rate: float) -> float:
    total_price = total_price * item_count
    discount_rate = discount_rate / 100
    total_price = total_price - (total_price * discount_rate)
    return total_price
"""

_BAD_NAME_SNIPPET_3 = """\
def compute_shipping(total_price: float, item_count: int, discount_rate: float) -> float:
    base = total_price * item_count
    discount_rate = min(discount_rate, 0.5)
    total_price = base * (1 - discount_rate)
    return total_price
"""

_DOCSTRING_SNIPPET_1 = """\
def calculate_total(price: float, quantity: int, discount: float) -> float:
    \"\"\"Calculate the total price after applying discount.\"\"\"
    subtotal = price * quantity
    return subtotal * (1 - discount)
"""

_DOCSTRING_SNIPPET_2 = """\
def format_address(street: str, city: str, zip_code: str) -> str:
    \"\"\"Calculate the total price after applying discount.\"\"\"
    return f"{street}, {city} {zip_code}"
"""

_DOCSTRING_SNIPPET_3 = """\
def parse_date(date_str: str) -> tuple:
    \"\"\"Calculate the total price after applying discount.\"\"\"
    parts = date_str.split("-")
    return int(parts[0]), int(parts[1]), int(parts[2])
"""

_TEST_SNIPPET_1 = """\
def create_user(name: str, email: str) -> dict:
    return {"name": name, "email": email, "active": True}


def test_create_user():
    user = create_user("Alice", "alice@example.com")
    assert user["name"] == "Alice"
    assert user["active"] is True
"""

_TEST_SNIPPET_2 = """\
def calculate_discount(price: float, pct: float) -> float:
    return price * (1 - pct / 100)


def test_calculate_discount():
    assert calculate_discount(100.0, 10.0) == 90.0
"""

_TEST_SNIPPET_3 = """\
def validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]


def test_validate_email():
    assert validate_email("a@b.com") is True
    assert validate_email("bad") is False
"""

_TEST_SNIPPET_4 = """\
def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def test_hash_password():
    result = hash_password("secret")
    assert len(result) == 64
"""

_TEST_SNIPPET_5 = """\
def paginate(items: list, page: int, size: int) -> list:
    start = (page - 1) * size
    return items[start:start + size]


def test_paginate():
    items = list(range(10))
    assert paginate(items, 1, 3) == [0, 1, 2]
"""

_TEST_SNIPPET_6 = """\
def slugify(text: str) -> str:
    return text.lower().replace(" ", "-")


def test_slugify():
    assert slugify("Hello World") == "hello-world"
"""

# ---------------------------------------------------------------------------
# 4 original clean diffs — bug_type = what the agent might FALSELY flag
# ---------------------------------------------------------------------------

_CLEAN_SECURITY_1 = """\
--- a/auth.py
+++ b/auth.py
@@ -1,8 +1,12 @@
 import os
 import hashlib
+import secrets

 def authenticate(username: str, password: str) -> bool:
-    stored_hash = db.get_password_hash(username)
+    stored_hash = db.get_password_hash(username)
+    if stored_hash is None:
+        return False
     salt = os.environ.get("PASSWORD_SALT", "")
     candidate = hashlib.sha256((password + salt).encode()).hexdigest()
     return secrets.compare_digest(candidate, stored_hash)
"""

_CLEAN_SECURITY_2 = """\
--- a/api.py
+++ b/api.py
@@ -3,6 +3,10 @@
 from flask import request, jsonify

 @app.route("/search")
-def search():
-    term = request.args.get("q", "")
-    results = db.search(term)
+def search():
+    term = request.args.get("q", "").strip()
+    if not term or len(term) > 100:
+        return jsonify({"error": "Invalid query"}), 400
+    results = db.search_safe(term)
     return jsonify(results)
"""

_CLEAN_STYLE_1 = """\
--- a/utils.py
+++ b/utils.py
@@ -1,5 +1,10 @@
+def format_currency(amount: float, symbol: str = "$") -> str:
+    \"\"\"Format a numeric amount as a currency string.\"\"\"
+    return f"{symbol}{amount:,.2f}"
+
+
 def calculate_tax(price: float, rate: float) -> float:
     \"\"\"Return the tax amount for a given price and tax rate.\"\"\"
     return round(price * rate, 2)
"""

_CLEAN_TESTS_1 = """\
--- a/orders.py
+++ b/orders.py
@@ -1,8 +1,16 @@
 def cancel_order(order_id: int) -> bool:
     order = db.get_order(order_id)
     if order is None:
         return False
     db.update_status(order_id, "cancelled")
     return True
+
+
+def test_cancel_order():
+    order_id = db.create_order({"item": "book", "qty": 1})
+    result = cancel_order(order_id)
+    assert result is True
+    assert db.get_order(order_id)["status"] == "cancelled"
"""

# ---------------------------------------------------------------------------
# 5 subtle bug diffs — harder patterns the agent must reason about
# ---------------------------------------------------------------------------

# SQL via f-string (no "+" concatenation, harder to spot)
_SUBTLE_SQL_FSTRING = """\
--- a/reports.py
+++ b/reports.py
@@ -3,5 +3,5 @@
 def get_report(report_id: str):
     conn = sqlite3.connect("app.db")
     cursor = conn.cursor()
-    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
+    cursor.execute(f"SELECT * FROM reports WHERE id = {report_id}")
     return cursor.fetchone()
"""

# Secret buried inside a config dict value (not a bare assignment)
_SUBTLE_SECRET_IN_DICT = """\
--- a/settings.py
+++ b/settings.py
@@ -1,5 +1,11 @@
 import os

+CONFIG = {
+    "api_key": "sk-live-xK9mP2qR7nL4wZ8vB3cY",
+    "timeout": 30,
+    "retry_count": 3,
+}
+
 def get_settings():
     return {
         "host": os.environ.get("HOST", "localhost"),
"""

# Docstring present but content is just "TODO" — technically has one, semantically absent
_SUBTLE_TODO_DOCSTRING = """\
--- a/payments.py
+++ b/payments.py
@@ -1,4 +1,9 @@
+def process_payment(amount: float, card_token: str) -> dict:
+    \"\"\"TODO\"\"\"
+    charge = stripe.charge(amount=amount, source=card_token)
+    return {"status": charge.status, "id": charge.id}
+
+
 def refund_payment(charge_id: str) -> bool:
     \"\"\"Refund a previously processed payment.\"\"\"
     return stripe.refund(charge_id).status == "succeeded"
"""

# Single-letter variable buried inside an otherwise clean function
_SUBTLE_BAD_VAR_IN_CONTEXT = """\
--- a/auth.py
+++ b/auth.py
@@ -3,6 +3,6 @@
 MAX_ATTEMPTS = 5

 def check_login_attempts(user_id: int) -> bool:
-    attempts = db.get_login_attempts(user_id)
-    return attempts < MAX_ATTEMPTS
+    n = db.get_login_attempts(user_id)
+    return n < MAX_ATTEMPTS
"""

# New class method added with no test — harder than a free function
_SUBTLE_MISSING_CLASS_METHOD_TEST = """\
--- a/cart.py
+++ b/cart.py
@@ -8,3 +8,10 @@
 class Cart:
     def add_item(self, item: dict) -> None:
         self.items.append(item)
+
+    def apply_coupon(self, code: str) -> float:
+        coupon = db.get_coupon(code)
+        if coupon and coupon["active"]:
+            self.discount = coupon["value"]
+            return coupon["value"]
+        return 0.0
"""

# ---------------------------------------------------------------------------
# 5 adversarial clean diffs — LOOK suspicious but are actually correct
# bug_type = what the agent is most likely to falsely flag them as
# ---------------------------------------------------------------------------

# Parameterized query that mentions "user_id" — safe, but looks like injection target
_ADV_CLEAN_PARAMETERIZED_SQL = """\
--- a/users.py
+++ b/users.py
@@ -1,5 +1,10 @@
 import sqlite3

+def get_profile(user_id: int) -> dict:
+    conn = sqlite3.connect("app.db")
+    cursor = conn.cursor()
+    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
+    return cursor.fetchone()
+
 def list_users() -> list:
     conn = sqlite3.connect("app.db")
     return conn.execute("SELECT id, name FROM users").fetchall()
"""

# password_hash variable that is actually hashed with bcrypt — not a plaintext secret
_ADV_CLEAN_PASSWORD_HASH = """\
--- a/auth.py
+++ b/auth.py
@@ -1,5 +1,12 @@
 import bcrypt

+def store_password(user_id: int, plaintext: str) -> None:
+    \"\"\"Hash password with bcrypt before storing; never stores plaintext.\"\"\"
+    password_hash = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt())
+    db.execute(
+        "UPDATE users SET password_hash = ? WHERE id = ?",
+        (password_hash, user_id),
+    )
+
 def verify_password(plaintext: str, stored_hash: bytes) -> bool:
     return bcrypt.checkpw(plaintext.encode(), stored_hash)
"""

# validate_input that genuinely validates — agent should see it IS safe
_ADV_CLEAN_VALIDATE_INPUT = """\
--- a/forms.py
+++ b/forms.py
@@ -1,4 +1,14 @@
 import re

+def validate_input(value: str, field_name: str) -> str:
+    \"\"\"Sanitize and validate a user-supplied string field.\"\"\"
+    if not value or not isinstance(value, str):
+        raise ValueError(f"{field_name} must be a non-empty string")
+    if len(value) > 500:
+        raise ValueError(f"{field_name} exceeds maximum length")
+    if re.search(r"[<>\"';()&+]", value):
+        raise ValueError(f"{field_name} contains disallowed characters")
+    return value.strip()
+
 def process_form(data: dict) -> dict:
     return {k: validate_input(v, k) for k, v in data.items()}
"""

# Long but fully descriptive function name with a proper docstring — no style issue
_ADV_CLEAN_GOOD_NAMES = """\
--- a/reports.py
+++ b/reports.py
@@ -1,4 +1,14 @@
+def calculate_monthly_revenue_by_region(
+    transactions: list,
+    region_code: str,
+    month: int,
+    year: int,
+) -> float:
+    \"\"\"Calculate total revenue for a specific region and calendar month.\"\"\"
+    return sum(
+        t["amount"] for t in transactions
+        if t["region"] == region_code
+        and t["month"] == month
+        and t["year"] == year
+    )
+
 def get_summary(data: list) -> dict:
     \"\"\"Summarize a list of data records.\"\"\"
     return {"total": sum(d["value"] for d in data), "count": len(data)}
"""

# New function that already ships with its own test
_ADV_CLEAN_HAS_TEST = """\
--- a/inventory.py
+++ b/inventory.py
@@ -3,3 +3,14 @@
 def get_stock(item_id: int) -> int:
     return db.get("stock", item_id, default=0)
+
+
+def restock(item_id: int, quantity: int) -> bool:
+    \"\"\"Increase stock level for an item; returns False for non-positive qty.\"\"\"
+    if quantity <= 0:
+        return False
+    current = get_stock(item_id)
+    db.set("stock", item_id, current + quantity)
+    return True
+
+
+def test_restock():
+    result = restock(42, 10)
+    assert result is True
"""

# ---------------------------------------------------------------------------
# Build the dataset
# ---------------------------------------------------------------------------

def _case(injected: dict, expected_agent: str) -> dict:
    return {
        "diff": injected["diff"],
        "bug_type": injected["bug_type"],
        "bug_line": injected["bug_line"],
        "description": injected["description"],
        "expected_agent": expected_agent,
        "should_find": True,
    }


def _subtle_case(
    diff: str,
    bug_type: str,
    bug_line: int,
    description: str,
    expected_agent: str,
) -> dict:
    return {
        "diff": diff,
        "bug_type": bug_type,
        "bug_line": bug_line,
        "description": description,
        "expected_agent": expected_agent,
        "should_find": True,
    }


def _clean_case(diff: str, suspected_bug_type: str, expected_agent: str) -> dict:
    # suspected_bug_type = what the agent might falsely flag this clean code as;
    # used by the scorer to detect false positives via keyword matching.
    return {
        "diff": diff,
        "bug_type": suspected_bug_type,
        "bug_line": -1,
        "description": f"Clean diff — no {suspected_bug_type} present",
        "expected_agent": expected_agent,
        "should_find": False,
    }


DATASET = [
    # ── Security: sql_injection (3) ──────────────────────────────────────────
    _case(inject_bug(_SQL_SNIPPET_1, "sql_injection"), "security"),
    _case(inject_bug(_SQL_SNIPPET_2, "sql_injection"), "security"),
    _case(inject_bug(_SQL_SNIPPET_3, "sql_injection"), "security"),

    # ── Security: hardcoded_secret (3) ───────────────────────────────────────
    _case(inject_bug(_SECRET_SNIPPET_1, "hardcoded_secret"), "security"),
    _case(inject_bug(_SECRET_SNIPPET_2, "hardcoded_secret"), "security"),
    _case(inject_bug(_SECRET_SNIPPET_3, "hardcoded_secret"), "security"),

    # ── Security: missing_input_validation (2) ───────────────────────────────
    _case(inject_bug(_VALIDATION_SNIPPET_1, "missing_input_validation"), "security"),
    _case(inject_bug(_VALIDATION_SNIPPET_2, "missing_input_validation"), "security"),

    # ── Security: subtle bugs (2) ────────────────────────────────────────────
    _subtle_case(_SUBTLE_SQL_FSTRING, "sql_injection", 8,
                 "SQL injection via f-string interpolation (no + operator)", "security"),
    _subtle_case(_SUBTLE_SECRET_IN_DICT, "hardcoded_secret", 7,
                 "API key hardcoded inside a dict literal, not a bare assignment", "security"),

    # ── Security: clean (2 original + 3 adversarial) ─────────────────────────
    _clean_case(_CLEAN_SECURITY_1, "hardcoded_secret", "security"),
    _clean_case(_CLEAN_SECURITY_2, "missing_input_validation", "security"),
    _clean_case(_ADV_CLEAN_PARAMETERIZED_SQL, "sql_injection", "security"),
    _clean_case(_ADV_CLEAN_PASSWORD_HASH, "hardcoded_secret", "security"),
    _clean_case(_ADV_CLEAN_VALIDATE_INPUT, "missing_input_validation", "security"),

    # ── Style: bad_variable_name (3) ─────────────────────────────────────────
    _case(inject_bug(_BAD_NAME_SNIPPET_1, "bad_variable_name"), "style"),
    _case(inject_bug(_BAD_NAME_SNIPPET_2, "bad_variable_name"), "style"),
    _case(inject_bug(_BAD_NAME_SNIPPET_3, "bad_variable_name"), "style"),

    # ── Style: missing_docstring (3) ─────────────────────────────────────────
    _case(inject_bug(_DOCSTRING_SNIPPET_1, "missing_docstring"), "style"),
    _case(inject_bug(_DOCSTRING_SNIPPET_2, "missing_docstring"), "style"),
    _case(inject_bug(_DOCSTRING_SNIPPET_3, "missing_docstring"), "style"),

    # ── Style: subtle bugs (2) ───────────────────────────────────────────────
    _subtle_case(_SUBTLE_TODO_DOCSTRING, "missing_docstring", 6,
                 'Docstring present but contains only "TODO" — meaningless placeholder', "style"),
    _subtle_case(_SUBTLE_BAD_VAR_IN_CONTEXT, "bad_variable_name", 7,
                 "Single-letter variable `n` buried inside an otherwise clean function", "style"),

    # ── Style: clean (1 original + 1 adversarial) ────────────────────────────
    _clean_case(_CLEAN_STYLE_1, "missing_docstring", "style"),
    _clean_case(_ADV_CLEAN_GOOD_NAMES, "bad_variable_name", "style"),

    # ── Tests: missing_test (6) ──────────────────────────────────────────────
    _case(inject_bug(_TEST_SNIPPET_1, "missing_test"), "tests"),
    _case(inject_bug(_TEST_SNIPPET_2, "missing_test"), "tests"),
    _case(inject_bug(_TEST_SNIPPET_3, "missing_test"), "tests"),
    _case(inject_bug(_TEST_SNIPPET_4, "missing_test"), "tests"),
    _case(inject_bug(_TEST_SNIPPET_5, "missing_test"), "tests"),
    _case(inject_bug(_TEST_SNIPPET_6, "missing_test"), "tests"),

    # ── Tests: subtle bugs (1) ───────────────────────────────────────────────
    _subtle_case(_SUBTLE_MISSING_CLASS_METHOD_TEST, "missing_test", 12,
                 "New class method apply_coupon added with no corresponding test", "tests"),

    # ── Tests: clean (1 original + 1 adversarial) ────────────────────────────
    _clean_case(_CLEAN_TESTS_1, "missing_test", "tests"),
    _clean_case(_ADV_CLEAN_HAS_TEST, "missing_test", "tests"),
]
