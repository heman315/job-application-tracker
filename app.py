from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                role TEXT,
                status TEXT,
                link TEXT,
                deadline TEXT
                )""")
    conn.commit()
    conn.close()

init_db()


# -----------------------------
# Home Page - Show Applications
# -----------------------------
@app.route("/")
def home():
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications")
    data = c.fetchall()
    conn.close()
    return render_template("home.html", data=data)


# -----------------------------
# Add Job Application
# -----------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        status = request.form["status"]
        link = request.form["link"]
        deadline = request.form["deadline"]

        conn = sqlite3.connect("jobs.db")
        c = conn.cursor()
        c.execute("INSERT INTO applications (company, role, status, link, deadline) VALUES (?, ?, ?, ?, ?)",
                  (company, role, status, link, deadline))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()

    if request.method == 'POST':
        company = request.form['company']
        role = request.form['role']
        status = request.form['status']
        link = request.form['link']
        deadline = request.form['deadline']

        c.execute("""
            UPDATE applications
            SET company=?, role=?, status=?, link=?, deadline=?
            WHERE id=?
        """, (company, role, status, link, deadline, id))
        conn.commit()
        conn.close()
        return redirect("/")

    # GET request - fetch job
    c.execute("SELECT * FROM applications WHERE id=?", (id,))
    job = c.fetchone()
    conn.close()
    return render_template('edit.html', job=job)
# -----------------------------
# Delete Application
# -----------------------------
@app.route("/delete/<int:app_id>")
def delete(app_id):
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("DELETE FROM applications WHERE id=?", (app_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()

    # Count total
    c.execute("SELECT COUNT(*) FROM applications")
    total = c.fetchone()[0]

    # Count each status
    c.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    stats = c.fetchall()

    # Upcoming deadlines
    c.execute("SELECT company, role, deadline FROM applications WHERE deadline != '' ORDER BY deadline LIMIT 5")
    deadlines = c.fetchall()

    conn.close()
    return render_template("dashboard.html", total=total, stats=stats, deadlines=deadlines)
# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)