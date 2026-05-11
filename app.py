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
    conn.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rider_name TEXT NOT NULL,
        team_name TEXT NOT NULL,
        race_id INTEGER,
        email TEXT NOT NULL,
        FOREIGN KEY (race_id) REFERENCES races (id)
    )
    """)

    team_count = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]

    if team_count == 0:
        conn.execute("INSERT INTO teams (name, city) VALUES ('MX Team', 'Jelgava')")
        conn.execute("INSERT INTO teams (name, city) VALUES ('Speed Riders', 'Rīga')")

        conn.execute("INSERT INTO riders (name, age, team_id) VALUES ('Martins Valainis', 18, 1)")
        conn.execute("INSERT INTO riders (name, age, team_id) VALUES ('Jānis Ozols', 17, 2)")

        races = [
            ("Latvijas BMX kausa 1. posms", "2026-04-18", "Jelgava"),
            ("Latvijas BMX kausa 2. posms", "2026-04-19", "Jelgava"),
            ("Latvijas BMX kausa 3. posms", "2026-05-09", "Mārupe"),
            ("Latvijas BMX kausa 4. posms", "2026-05-10", "Mārupe"),
            ("Latvijas BMX čempionāts", "2026-06-06", "Valmiera"),
            ("Latvijas BMX kausa 5. posms", "2026-06-07", "Valmiera"),
            ("Latvijas BMX kausa 6. posms", "2026-07-04", "Smiltene"),
            ("Latvijas BMX kausa 7. posms", "2026-07-05", "Smiltene"),
            ("Latvijas BMX kausa 8. posms", "2026-08-08", "Rīga"),
            ("Latvijas BMX kausa 9. posms", "2026-08-09", "Rīga"),
            ("Latvijas BMX kausa 10. posms", "2026-09-05", "Madona"),
            ("Latvijas BMX kausa 11. posms", "2026-09-06", "Madona")
        ]

        for race in races:
            conn.execute(
                "INSERT INTO races (title, race_date, location) VALUES (?, ?, ?)",
                race
            )

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
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        team_name = request.form["team_name"]

        conn = get_db_connection()

        existing_team = conn.execute(
            "SELECT id FROM teams WHERE name = ?",
            (team_name,)
        ).fetchone()

        if existing_team:
            team_id = existing_team["id"]
        else:
            conn.execute(
                "INSERT INTO teams (name, city) VALUES (?, ?)",
                (team_name, "Nav norādīts")
            )
            team_id = conn.execute(
                "SELECT id FROM teams WHERE name = ?",
                (team_name,)
            ).fetchone()["id"]

        conn.execute(
            "INSERT INTO riders (name, age, team_id) VALUES (?, ?, ?)",
            (name, age, team_id)
        )

        conn.commit()
        conn.close()

        return redirect("/riders")

    return render_template("add_rider.html")


@app.route("/edit_rider/<int:id>", methods=["GET", "POST"])
def edit_rider(id):
    conn = get_db_connection()

    rider = conn.execute("""
        SELECT riders.id, riders.name, riders.age, teams.name AS team_name
        FROM riders
        LEFT JOIN teams ON riders.team_id = teams.id
        WHERE riders.id = ?
    """, (id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        team_name = request.form["team_name"]

        existing_team = conn.execute(
            "SELECT id FROM teams WHERE name = ?",
            (team_name,)
        ).fetchone()

        if existing_team:
            team_id = existing_team["id"]
        else:
            conn.execute(
                "INSERT INTO teams (name, city) VALUES (?, ?)",
                (team_name, "Nav norādīts")
            )
            team_id = conn.execute(
                "SELECT id FROM teams WHERE name = ?",
                (team_name,)
            ).fetchone()["id"]

        conn.execute(
            "UPDATE riders SET name = ?, age = ?, team_id = ? WHERE id = ?",
            (name, age, team_id, id)
        )

        conn.commit()
        conn.close()

        return redirect("/riders")

    conn.close()
    return render_template("edit_rider.html", rider=rider)


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

@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    conn = get_db_connection()
    races = conn.execute("SELECT * FROM races").fetchall()

    if request.method == "POST":
        rider_name = request.form["rider_name"]
        team_name = request.form["team_name"]
        email = request.form["email"]
        race_id = request.form["race_id"]

        conn.execute(
            "INSERT INTO registrations (rider_name, team_name, email, race_id) VALUES (?, ?, ?, ?)",
            (rider_name, team_name, email, race_id)
        )

        conn.commit()
        conn.close()

        return redirect("/races")

    conn.close()
    return render_template("register.html", races=races)
if __name__ == "__main__":
    init_db()
    app.run(debug=True)