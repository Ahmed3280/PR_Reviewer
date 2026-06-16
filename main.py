from agents.security import run_security_review
from agents.style import run_style_review
from agents.tests import run_test_review

# A fake diff with an obvious security bug planted in it
test_diff = """
-    query = "SELECT * FROM users WHERE id = " + user_id
+    password = "admin123"
+    db.execute("DELETE FROM users WHERE id = " + user_id)
+    def x(a, b, c, d, e):
+        pass
"""

print("Security")
print(run_security_review(test_diff))

print("Style")
print(run_style_review(test_diff))

print("Tests")
print(run_test_review(test_diff))