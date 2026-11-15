import sqlite3

conn = sqlite3.connect('exam_seat.db')
cur = conn.cursor()

def add_col(table, col_name, col_type):
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
        print(f"Added {col_name} to {table}")
    except Exception as e:
        print(f"Skipped {col_name} on {table}: {e}")

add_col('students', 'admission_year', 'INTEGER')
add_col('students', 'regulation', "VARCHAR(20) DEFAULT 'R2021'")
add_col('students', 'student_status', "VARCHAR(20) DEFAULT 'Regular'")

add_col('examinations', 'exam_type', "VARCHAR(20) DEFAULT 'Current'")
add_col('examinations', 'eligible_semester', 'INTEGER')
add_col('examinations', 'regulation', 'VARCHAR(20)')

cur.execute("""
CREATE TABLE IF NOT EXISTS arrear_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    register_number VARCHAR(20) NOT NULL,
    department_code VARCHAR(10) NOT NULL,
    subject_code VARCHAR(20) NOT NULL,
    subject_name VARCHAR(100),
    semester INTEGER,
    regulation VARCHAR(20),
    attempt_count INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")
print("arrear_records table ensured")

conn.commit()
conn.close()
