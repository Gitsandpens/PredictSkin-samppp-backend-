"""Small email + password login using only the Python standard library.

Passwords are stored as salted PBKDF2 hashes (never the password itself).
Login returns a signed token that the frontend sends with each request.
"""
import base64, hashlib, hmac, json, os, re, secrets, sqlite3, time
from pathlib import Path
from typing import Optional
from fastapi import Header, HTTPException

DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent.parent / "users.db"))
SECRET = os.getenv("AUTH_SECRET") or secrets.token_hex(32)  # set AUTH_SECRET so logins survive restarts
TOKEN_TTL = 7 * 24 * 3600
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = _connect()
    try:
        con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, "
                    "email TEXT UNIQUE NOT NULL, salt BLOB NOT NULL, pw_hash BLOB NOT NULL, created REAL NOT NULL)")
        con.commit()
    finally:
        con.close()


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)


def _public(row) -> dict:
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def create_user(name: str, email: str, password: str) -> dict:
    name, email = name.strip(), email.strip().lower()
    if not 1 <= len(name) <= 60:
        raise HTTPException(400, "Please enter your name.")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    if not 8 <= len(password) <= 128:
        raise HTTPException(400, "Password must be at least 8 characters.")
    salt = os.urandom(16)
    con = _connect()
    try:
        cur = con.execute("INSERT INTO users (name, email, salt, pw_hash, created) VALUES (?,?,?,?,?)",
                          (name, email, salt, _hash(password, salt), time.time()))
        con.commit()
        return {"id": cur.lastrowid, "name": name, "email": email}
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with this email already exists.")
    finally:
        con.close()


def check_login(email: str, password: str) -> dict:
    con = _connect()
    try:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    finally:
        con.close()
    salt = row["salt"] if row else b"0" * 16
    ok = hmac.compare_digest(_hash(password, salt), row["pw_hash"] if row else b"x" * 32)
    if not row or not ok:
        raise HTTPException(401, "Incorrect email or password.")
    return _public(row)


def _sign(body: str) -> str:
    return hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()


def make_token(user: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps({**user, "exp": time.time() + TOKEN_TTL}).encode()).decode()
    return f"{body}.{_sign(body)}"


def current_user(authorization: Optional[str] = Header(None)) -> dict:
    """FastAPI dependency: returns the logged-in user or raises 401."""
    try:
        scheme, token = (authorization or "").split(" ", 1)
        body, sig = token.split(".", 1)
        if scheme.lower() != "bearer" or not hmac.compare_digest(sig, _sign(body)):
            raise ValueError
        data = json.loads(base64.urlsafe_b64decode(body))
        if data["exp"] < time.time():
            raise ValueError
        return {k: data[k] for k in ("id", "name", "email")}
    except Exception:
        raise HTTPException(401, "Please log in to continue.")
