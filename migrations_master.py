import sqlite3

def upgrade():
    con = sqlite3.connect('exam_seat.db')
    cur = con.cursor()
    
    # 1. Examination status history
    cur.execute('''
    CREATE TABLE IF NOT EXISTS examination_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        examination_id INTEGER NOT NULL,
        previous_date VARCHAR(20),
        previous_session VARCHAR(50),
        new_date VARCHAR(20),
        new_session VARCHAR(50),
        previous_status VARCHAR(50),
        new_status VARCHAR(50) NOT NULL,
        reason TEXT,
        updated_by VARCHAR(80) DEFAULT 'Admin',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(examination_id) REFERENCES examinations(id) ON DELETE CASCADE
    );
    ''')

    # 2. Activity logs columns
    cols = [c[1] for c in cur.execute('PRAGMA table_info(activity_logs)').fetchall()]
    if 'activity_type' not in cols:
        cur.execute('ALTER TABLE activity_logs ADD COLUMN activity_type VARCHAR(50)')
    if 'module' not in cols:
        cur.execute('ALTER TABLE activity_logs ADD COLUMN module VARCHAR(50)')
    if 'status' not in cols:
        cur.execute("ALTER TABLE activity_logs ADD COLUMN status VARCHAR(20) DEFAULT 'Success'")

    # 3. Examination columns
    exam_cols = [c[1] for c in cur.execute('PRAGMA table_info(examinations)').fetchall()]
    if 'original_exam_date' not in exam_cols:
        cur.execute('ALTER TABLE examinations ADD COLUMN original_exam_date VARCHAR(20)')
    if 'original_session' not in exam_cols:
        cur.execute('ALTER TABLE examinations ADD COLUMN original_session VARCHAR(50)')
    if 'postponed_date' not in exam_cols:
        cur.execute('ALTER TABLE examinations ADD COLUMN postponed_date VARCHAR(20)')
    if 'postponed_reason' not in exam_cols:
        cur.execute('ALTER TABLE examinations ADD COLUMN postponed_reason TEXT')
    if 'rescheduled_date' not in exam_cols:
        cur.execute('ALTER TABLE examinations ADD COLUMN rescheduled_date VARCHAR(20)')
    if 'rescheduled_reason' not in exam_cols:
        cur.execute('ALTER TABLE examinations ADD COLUMN rescheduled_reason TEXT')

        # 4. Examination Department Subjects columns
    eds_cols = [c[1] for c in cur.execute('PRAGMA table_info(examination_department_subjects)').fetchall()]
    if 'year' not in eds_cols:
        cur.execute('ALTER TABLE examination_department_subjects ADD COLUMN year VARCHAR(20)')
    if 'semester' not in eds_cols:
        cur.execute('ALTER TABLE examination_department_subjects ADD COLUMN semester VARCHAR(20)')

        # 5. Students DOB column
    std_cols = [c[1] for c in cur.execute('PRAGMA table_info(students)').fetchall()]
    if 'dob' not in std_cols:
        cur.execute('ALTER TABLE students ADD COLUMN dob VARCHAR(30)')

    con.commit()
    con.close()
    print("Database schema successfully upgraded.")

if __name__ == '__main__':
    upgrade()
