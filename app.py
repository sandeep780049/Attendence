from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        credential_id TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        date TEXT,
                        time TEXT)''')
    conn.commit()
    conn.close()

# Home (student page)
@app.route('/')
def index():
    return render_template("index.html")

# Admin dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT students.name, attendance.date, attendance.time
                      FROM attendance 
                      JOIN students ON students.id = attendance.student_id""")
    records = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", records=records)

# Register student (simulate WebAuthn for now)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get("name")
    credential_id = data.get("credential_id")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (name, credential_id) VALUES (?, ?)", (name, credential_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"message": "Student already registered"}), 400
    conn.close()
    return jsonify({"message": f"{name} registered successfully!"})

# Mark attendance
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    credential_id = data.get("credential_id")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students WHERE credential_id=?", (credential_id,))
    student = cursor.fetchone()

    if student:
        student_id, name = student
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        cursor.execute("INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)", (student_id, date, time))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Attendance marked for {name} at {time}"})
    else:
        conn.close()
        return jsonify({"message": "Student not found"}), 404

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
