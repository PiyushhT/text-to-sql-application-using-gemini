import streamlit as st
import google.generativeai as genai
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY not found in environment variables. Please check your .env file.")
    st.stop()

# Configure Gemini AI
genai.configure(api_key=api_key)
MODEL_NAME = "gemini-1.5-flash-latest"  # Keeping the original model
model = genai.GenerativeModel(MODEL_NAME)

# Initialize Database
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
            ("Charlie", 70000),
            ("David", 82000),
            ("Eve", 91000)
        ])
        conn.commit()
    
    conn.close()

# Convert Text to SQL
def text_to_sql(user_input):
    prompt = f"Convert this query to SQL for SQLite: {user_input}. Ensure valid SQL syntax and only generate SELECT statements."
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Cleanup SQL query
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        if not sql_query.lower().startswith("select"):
            return None, "❌ Error: AI generated a non-SELECT query. Only SELECT queries are allowed."
        
        return sql_query, None
    except Exception as e:
        return None, f"⚠️ Error generating SQL: {str(e)}"

# Execute SQL Query
def execute_sql(query):
    conn = sqlite3.connect("my_database.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]  # Get column names
        result = cursor.fetchall()
        conn.close()
        
        # Rename columns for better clarity
        renamed_columns = ["Employee ID" if col == "id" else "Employee Name" if col == "name" else "Salary" if col == "salary" else col for col in columns]
        
        return result, renamed_columns, None
    except sqlite3.Error as e:
        conn.close()
        return None, None, f"⚠️ Error executing SQL: {str(e)}"

# Streamlit UI
st.title("🧠 AI-Powered Text-to-SQL Converter")
st.subheader("Enter your natural language query:")

initialize_db()

user_query = st.text_input("Your Query:")

if st.button("Generate SQL & Execute"):
    if user_query:
        sql_query, error = text_to_sql(user_query)
        
        if error:
            st.error(error)
        elif sql_query:
            data, columns, db_error = execute_sql(sql_query)
            
            st.code(sql_query, language="sql")
            st.write("### Query Result:")
            if db_error:
                st.error(db_error)
            else:
                if data:
                    df = pd.DataFrame(data, columns=columns)
                    st.dataframe(df)  # Display results as a table
                else:
                    st.info("ℹ️ No results found.")
        else:
            st.error("⚠️ Generated query is invalid or an error occurred.")
    else:
        st.warning("⚠️ Please enter a query to convert.")
