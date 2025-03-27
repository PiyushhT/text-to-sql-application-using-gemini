import google.generativeai as genai
import os
import sqlite3
import re  # ✅ Backticks remove karne ke liye import kiya
from dotenv import load_dotenv

# ✅ API Key Load Karo
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)

# ✅ Sahi Model Choose Karo
MODEL_NAME = "gemini-1.5-flash-latest"  # "gemini-1.5-pro-latest" bhi try kar sakte ho
model = genai.GenerativeModel(MODEL_NAME)

# ✅ Database Initialize Karo
def initialize_db():
    conn = sqlite3.connect("my_database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            salary INTEGER
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO employees (name, salary) VALUES (?, ?)", [
            ("Alice", 60000),
            ("Bob", 45000),
            ("Charlie", 75000)
        ])
        conn.commit()
    
    conn.close()

# ✅ Text ko SQL me Convert Karo
def text_to_sql(user_input):
    prompt = f"Convert this query to SQL for SQLite: {user_input}. Ensure valid SQL syntax."
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # ✅ Remove ```sql and ```
        sql_query = re.sub(r"```sql|```", "", sql_query).strip()

        print("🟢 Generated SQL Query:", sql_query)
        return sql_query
    except Exception as e:
        print("❌ Error generating SQL:", str(e))
        return None

# ✅ SQL Execute Karo
def execute_sql(query):
    conn = sqlite3.connect("my_database.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        conn.close()
        return f"❌ Error executing SQL: {str(e)}"

# --- 🔹 Main Execution ---
initialize_db()

user_query = "Show all employees earning more than 50000"
sql_query = text_to_sql(user_query)

if sql_query and sql_query.lower().startswith("select"):  # ✅ Sirf SELECT queries execute honi chahiye
    data = execute_sql(sql_query)
    print("✅ Query Result:", data)
else:
    print("❌ Generated query is not a valid SELECT statement or an error occurred.")
