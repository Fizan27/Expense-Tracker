import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

conn = sqlite3.connect("user.sqlite")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)")

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the email and password match a record in the database
        with sqlite3.connect("user.sqlite") as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)")
            cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cur.fetchone()

        if user:
            return redirect(url_for("home"))
        else:
            error = "Invalid email or password"

        return render_template("login.html", error=error)
    else:
        return render_template("login.html")

@app.route("/Register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]

        if password != password_confirm:
            error = "Passwords do not match. Please try again."
            return render_template("Register.html", error=error)

        # Insert the user data into the database
        with sqlite3.connect("user.sqlite") as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)")
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()

        return redirect(url_for("home"))
    else:
        return render_template("Register.html", error=error)

@app.route("/Home")
def home():
    return render_template('Home.html')

if __name__=='__main__':
    app.run(debug=True)