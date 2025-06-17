import sqlite3

conn = sqlite3.connect("db.sqlite")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    section TEXT,
    marks INTEGER
)
""")
cursor.executemany("INSERT INTO student (name, section, marks) VALUES (?, ?, ?)", [
    ("Alice", "math", 17),
    ("Bob", "science", 12),
    ("Charlie", "math", 9),
])
conn.commit()
conn.close()
