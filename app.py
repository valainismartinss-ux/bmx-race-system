from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS riders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            race_date TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rider_id INTEGER,
            race_id INTEGER,
            place INTEGER NOT NULL,
            points INTEGER NOT NULL,
            FOREIGN KEY (rider_id) REFERENCES riders (id),
            FOREIGN KEY (race_id) REFERENCES races (id)
        )
    """)

    team_count = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]

    if team_count == 0:
        conn.execute("INSERT INTO teams (name, city) VALUES ('MX Team', 'Jelgava')")
        conn.execute("INSERT INTO teams (name, city) VALUES ('Speed Riders', 'Rīga')")

        conn.execute("INSERT INTO riders (name, age, team_id) VALUES ('Martins Valainis', 18, 1)")
        conn.execute("INSERT INTO riders (name, age, team_id) VALUES ('Jānis Ozols', 17, 2)")

        conn.execute("INSERT INTO races (title, race_date, location) VALUES ('Riga BMX Cup', '2026-05-15', 'Rīga')")
        conn.execute("INSERT INTO races (title, race_date, location) VALUES ('Latvia Open', '2026-06-01', 'Jelgava')")

        conn.execute("INSERT INTO results (rider_id, race_id, place, points) VALUES (1, 1, 1, 25)")
        conn.execute("INSERT INTO results (rider_id, race_id, place, points) VALUES (2, 1, 2, 18)")

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/riders")
def riders():
    conn = get_db_connection()
    riders = conn.execute("""
        SELECT riders.id, riders.name, riders.age, teams.name AS team_name
        FROM riders
        LEFT JOIN teams ON riders.team_id = teams.id
    """).fetchall()
    conn.close()
    return render_template("riders.html", riders=riders)
@app.route("/add_rider", methods=["GET", "POST"])
def add_rider():
    conn = get_db_connection()
    teams = conn.execute("SELECT * FROM teams").fetchall()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        team_id = request.form["team_id"]

        conn.execute(
            "INSERT INTO riders (name, age, team_id) VALUES (?, ?, ?)",
            (name, age, team_id)
        )
        conn.commit()
        conn.close()
        return redirect("/riders")

    conn.close()
    return render_template("add_rider.html", teams=teams)


@app.route("/edit_rider/<int:id>", methods=["GET", "POST"])
def edit_rider(id):
    conn = get_db_connection()
    rider = conn.execute("SELECT * FROM riders WHERE id = ?", (id,)).fetchone()
    teams = conn.execute("SELECT * FROM teams").fetchall()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        team_id = request.form["team_id"]

        conn.execute(
            "UPDATE riders SET name = ?, age = ?, team_id = ? WHERE id = ?",
            (name, age, team_id, id)
        )
        conn.commit()
        conn.close()
        return redirect("/riders")

    conn.close()
    return render_template("edit_rider.html", rider=rider, teams=teams)


@app.route("/delete_rider/<int:id>")
def delete_rider(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM riders WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/riders")

@app.route("/races")
def races():
    conn = get_db_connection()
    races = conn.execute("SELECT * FROM races").fetchall()
    conn.close()
    return render_template("races.html", races=races)

@app.route("/results")
def results():
    conn = get_db_connection()
    results = conn.execute("""
        SELECT results.place, results.points, riders.name AS rider_name, races.title AS race_title
        FROM results
        JOIN riders ON results.rider_id = riders.id
        JOIN races ON results.race_id = races.id
        ORDER BY results.place
    """).fetchall()
    conn.close()
    return render_template("results.html", results=results)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)