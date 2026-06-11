from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Create database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

register_page = """
<h2>Register</h2>
<form method="POST">
Username:<br>
<input name="username"><br><br>

Password:<br>
<input type="password" name="password"><br><br>

<button type="submit">Register</button>
</form>

<a href="/login">Login</a>
"""

login_page = """
<h2>Login</h2>
<form method="POST">
Username:<br>
<input name="username"><br><br>

Password:<br>
<input type="password" name="password"><br><br>

<button type="submit">Login</button>
</form>

<a href="/">Register</a>
"""

dashboard_page = """
<h2>Dashboard</h2>
<p>Welcome {{username}}</p>

<a href="/logout">Logout</a>
"""


@app.route("/", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3:
            return "Username too short"

        if len(password) < 8:
            return "Password must be at least 8 characters"

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        )

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            return "User already exists"

    return render_template_string(register_page)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            stored_hash = user[0]

            if bcrypt.checkpw(
                password.encode(),
                stored_hash
            ):
                session["user"] = username
                return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template_string(login_page)


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template_string(
        dashboard_page,
        username=session["user"]
    )


@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
