from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "dev-secret"

USER = {
    "email": "admin@example.com",
    "password": "password123"
}

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    email = request.form.get("email")
    password = request.form.get("password")

    if email == USER["email"] and password == USER["password"]:
        session["user"] = email
        return redirect("/dashboard")

    return "Invalid credentials"


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
