import sqlite3

# Database create karo
conn = sqlite3.connect("my_database.db")
cursor = conn.cursor()

# Employees table banao
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    salary INTEGER
)
""")

# Sample Data Insert Karo
cursor.executemany("INSERT INTO employees (name, salary) VALUES (?, ?)", [
    ("Alice", 60000),
    ("Bob", 45000),
    ("Charlie", 70000)
])

conn.commit()
conn.close()

print("✅ Database setup done!")