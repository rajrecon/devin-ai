import logging

from flask import Flask, flash, render_template, request, redirect, session, url_for
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Serializer used to create / validate password-reset tokens.
# Tokens are signed with the app's secret key and the "password-reset" salt
# so they cannot be confused with other signed values.
# ---------------------------------------------------------------------------
serializer = URLSafeTimedSerializer(app.secret_key)
RESET_TOKEN_SALT = "password-reset-salt"
RESET_TOKEN_MAX_AGE = 1800  # 30 minutes

# ---------------------------------------------------------------------------
# In-memory user store.  The password is now hashed at startup so it is never
# stored in plaintext.
# ---------------------------------------------------------------------------
USER = {
    "email": "admin@example.com",
    "password": generate_password_hash("password123"),
}


# ---- helpers ---------------------------------------------------------------

def generate_reset_token(email):
    """Return a URL-safe, time-limited token that encodes *email*."""
    return serializer.dumps(email, salt=RESET_TOKEN_SALT)


def verify_reset_token(token):
    """Decode *token* and return the email if valid, otherwise ``None``."""
    try:
        return serializer.loads(
            token,
            salt=RESET_TOKEN_SALT,
            max_age=RESET_TOKEN_MAX_AGE,
        )
    except (SignatureExpired, BadSignature):
        return None


# ---- routes ----------------------------------------------------------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    email = request.form.get("email")
    password = request.form.get("password")

    if email == USER["email"] and check_password_hash(USER["password"], password):
        session["user"] = email
        return redirect("/dashboard")

    flash("Invalid credentials.", "error")
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---- forgot / reset password ----------------------------------------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Show the forgot-password form and, on POST, generate a reset link."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        # Always show success to avoid leaking whether an email is registered.
        if email == USER["email"]:
            token = generate_reset_token(email)
            reset_url = url_for("reset_password", token=token, _external=True)
            # In production this would be sent via email; here we log it.
            logger.info("Password-reset link for %s: %s", email, reset_url)

        flash(
            "If that email is registered you will receive a reset link shortly.",
            "info",
        )
        return redirect("/forgot-password")

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Validate the token, then let the user set a new password."""
    email = verify_reset_token(token)
    if email is None:
        flash("The reset link is invalid or has expired.", "error")
        return redirect("/forgot-password")

    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("reset_password", token=token))

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("reset_password", token=token))

        USER["password"] = generate_password_hash(new_password)
        flash("Your password has been reset. Please log in.", "success")
        return redirect("/")

    return render_template("reset_password.html", token=token)


if __name__ == "__main__":
    app.run(debug=True)
