"""Agrogasm backend - Flask API for community posts.

Endpoints (all JSON):
    GET  /?limit=&offset=&q=&sort=&reliability=&type=
         -> {"data": {"posts": [...], "global": {"threshold": int}},
             "meta": {"total": int, "limit": int, "offset": int}}
    GET  /community/<pid>              -> {"post": {...}}
    POST /community/new                -> create post, body: {author, title, description, type?, image_url?, group_id?}
    POST /community/<pid>/vote         -> body: {direction: "up" | "down"}
    POST /community/<pid>/comment      -> body: {author, description}
    DELETE /community/<pid>            -> delete post + comments
    GET  /advisory/crop-calendar       -> {"month": int, "items": [{"crop", "action"}]}
    GET  /advisory/pest-watch          -> {"month": int, "items": [{"crop", "pest", "action"}]}
    GET  /advisory/spray               -> body: {wind, humidity, condition, rain_4h} -> verdict
    GET  /advisory/irrigation          -> body: {temp, condition, rainfall_mm} -> should irrigate
    GET  /advisory/seasonal            -> {"items": [{"severity", "text"}]}
    GET  /advisory/pesticide?q=       -> {"found": bool, "pesticide": {...}}
    GET  /market/prices?q=             -> {"prices": [{crop, market, price, unit}]}
    GET  /groups                       -> {"groups": [...]}
    POST /groups/new                   -> body: {name} -> {"group_id"}
    POST /groups/join                  -> body: {group_id, user_id?} -> {"message"}
    POST /uploads/photo                -> multipart -> {"url": "/static/uploads/..."}
    GET  /health                       -> {"status": "ok"}

Init DB explicitly with: flask --app agrogasm init-db
"""

import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, send_from_directory, current_app
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import crop_advisory
import market_data

load_dotenv()


def get_database_path() -> str:
    return os.getenv("AGROGASM_DB", "agrogasm.db")


def get_threshold() -> int:
    try:
        return int(os.getenv("AGROGASM_THRESHOLD", "10"))
    except ValueError:
        return 10


def get_frontend_origin() -> str:
    return os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5173")


app = Flask(__name__)
app.config["THRESHOLD"] = get_threshold()
CORS(app, resources={r"/*": {"origins": get_frontend_origin()}})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

SEED_POSTS = [
    {
        "pid": 0,
        "author": "taj",
        "title": "November: Time for spinach.",
        "description": "Time for spinach is november",
        "upvote": 420,
        "downvote": 0,
    },
    {
        "pid": 1,
        "author": "nishoy",
        "title": "Free tomato seeds distribution",
        "description": "Tomato seeds distribution at KB",
        "upvote": 69,
        "downvote": 17,
    },
    {
        "pid": 2,
        "author": "aflah",
        "title": "A third Title",
        "description": "Probably a nice description.",
        "upvote": 8,
        "downvote": 23,
    },
]

SEED_COMMENTS = [
    {
        "pid_title": "November: Time for spinach.",
        "author": "nishoy",
        "description": "This is an informative post and it'll surely help in my cultivation.",
        "upvote": 1,
        "downvote": 3,
    },
    {
        "pid_title": "Free tomato seeds distribution",
        "author": "rashid",
        "description": "Interesting, will try this on my plot.",
        "upvote": 4,
        "downvote": 0,
    },
    {
        "pid_title": "A third Title",
        "author": "taj",
        "description": "Source? This looks unverified.",
        "upvote": 4,
        "downvote": 0,
    },
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    pid INTEGER PRIMARY KEY,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    post_type TEXT NOT NULL DEFAULT 'general',
    image_url TEXT,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    upvote INTEGER NOT NULL DEFAULT 0,
    downvote INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid INTEGER NOT NULL REFERENCES posts(pid) ON DELETE CASCADE,
    author TEXT NOT NULL,
    description TEXT NOT NULL,
    upvote INTEGER NOT NULL DEFAULT 0,
    downvote INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS group_members (
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    joined_at TEXT NOT NULL,
    PRIMARY KEY (group_id, user_id)
);
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop TEXT NOT NULL,
    market TEXT NOT NULL,
    price REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'kg',
    observed_at TEXT NOT NULL
);
"""


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(get_database_path(), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.DatabaseError:
            pass
        conn.executescript(SCHEMA)
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(seed: bool = True):
    db = get_db()
    db.executescript(SCHEMA)
    if not seed:
        return
    count = db.execute("SELECT COUNT(*) AS c FROM posts").fetchone()["c"]
    if count == 0:
        now = datetime.now(timezone.utc).isoformat()
        for p in SEED_POSTS:
            db.execute(
                "INSERT INTO posts (author, title, description, post_type, upvote, downvote, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (p["author"], p["title"], p["description"],
                 "general", p["upvote"], p["downvote"], now),
            )
        for c in SEED_COMMENTS:
            # Seed pid maps to actual insert order pid via title lookup
            actual_pid = db.execute("SELECT pid FROM posts WHERE title = ? LIMIT 1", (c["pid_title"],)).fetchone()
            if actual_pid is None:
                continue
            pid_val = actual_pid["pid"]
            db.execute(
                "INSERT INTO comments (pid, author, description, upvote, downvote, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (pid_val, c["author"], c["description"],
                 c["upvote"], c["downvote"], now),
            )
        db.commit()
    # seed market prices
    pcount = db.execute("SELECT COUNT(*) AS c FROM prices").fetchone()["c"]
    if pcount == 0:
        for p in market_data.get_prices():
            db.execute(
                "INSERT INTO prices (crop, market, price, unit, observed_at) VALUES (?,?,?,?,?)",
                (p["crop"], p["market"], p["price"], p["unit"], p["date"]),
            )
        db.commit()
    # seed groups
    gcount = db.execute("SELECT COUNT(*) AS c FROM groups").fetchone()["c"]
    if gcount == 0:
        now = datetime.now(timezone.utc).isoformat()
        seed_groups = [
            ("Kottayam Central", "Farmers around Kottayam town"),
            ("Vaikom Area", "Vaikom block panchayat"),
            ("Kumarakom", "Kumarakom area - paddy and vegetables"),
            ("Changanassery", "Changanassery taluk"),
            ("Idukki Hills", "Spice farmers of Idukki"),
            ("Alappuzha Kuttanad", "Kuttanad paddy belt"),
        ]
        for name, desc in seed_groups:
            db.execute("INSERT INTO groups (name, description, created_at) VALUES (?,?,?)", (name, desc, now))
        db.commit()


@app.cli.command("init-db")
def init_db_command():
    """Create tables and seed demo data if empty."""
    init_db(seed=True)
    print(f"Database ready at {get_database_path()}")


@app.after_request
def set_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


def reliability_for(upvote: int, downvote: int, threshold=None) -> str:
    if threshold is None:
        threshold = get_threshold()
    total = upvote + downvote
    if total < threshold:
        return "new"
    if downvote == 0:
        return "reliable" if upvote > 0 else "new"
    score = (upvote / total) * 100
    if score >= 70:
        return "reliable"
    if score >= 40:
        return "unsure"
    return "unreliable"


def row_to_post(row: sqlite3.Row, comments: list, threshold=None) -> dict:
    if threshold is None:
        threshold = get_threshold()
    return {
        "pid": row["pid"],
        "author": row["author"],
        "title": row["title"],
        "description": row["description"],
        "post_type": row["post_type"],
        "image_url": row["image_url"],
        "group_id": row["group_id"],
        "upvote": row["upvote"],
        "downvote": row["downvote"],
        "reliability": reliability_for(row["upvote"], row["downvote"], threshold),
        "created_at": row["created_at"],
        "comments": comments,
    }


def error(message: str, status: int):
    return jsonify(error=message), status


VALID_SORTS = {"new", "top", "old"}
VALID_POST_TYPES = {"general", "pest_alert", "price_share", "equipment_rental", "advice"}


def get_all_posts(limit: int = 50, offset: int = 0, q: str = "",
                  sort: str = "new", reliability: str = "", post_type: str = "",
                  group_id: int | None = None):
    threshold = get_threshold()
    db = get_db()
    where = []
    params: list = []
    if q:
        where.append("(title LIKE ? OR description LIKE ? OR author LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like, like])
    if post_type:
        where.append("post_type = ?")
        params.append(post_type)
    if group_id is not None:
        where.append("group_id = ?")
        params.append(group_id)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    total = db.execute(f"SELECT COUNT(*) AS c FROM posts {where_sql}", params).fetchone()["c"]

    order = "pid DESC"
    if sort == "old":
        order = "pid ASC"
    elif sort == "top":
        order = "(upvote - downvote) DESC, pid DESC"

    rows = db.execute(
        f"SELECT * FROM posts {where_sql} ORDER BY {order} LIMIT ? OFFSET ?",
        (*params, limit, offset),
    ).fetchall()
    if not rows:
        return [], total
    pids = [r["pid"] for r in rows]
    placeholders = ",".join("?" for _ in pids)
    comment_rows = db.execute(
        f"SELECT * FROM comments WHERE pid IN ({placeholders}) ORDER BY id ASC", pids
    ).fetchall()
    by_pid: dict[int, list] = {}
    for c in comment_rows:
        by_pid.setdefault(c["pid"], []).append({
            "id": c["id"],
            "author": c["author"],
            "description": c["description"],
            "upvote": c["upvote"],
            "downvote": c["downvote"],
            "created_at": c["created_at"],
        })
    posts = [row_to_post(p, by_pid.get(p["pid"], []), threshold) for p in rows]
    if reliability:
        posts = [p for p in posts if p["reliability"] == reliability]
    return posts, total


@app.route("/", methods=["GET"])
def get_init_data():
    try:
        limit = min(int(request.args.get("limit", 50)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except ValueError:
        return error("limit and offset must be integers", 400)
    q = request.args.get("q", "").strip()[:100]
    sort = request.args.get("sort", "new")
    if sort not in VALID_SORTS:
        return error("sort must be one of new, old, top", 400)
    reliability = request.args.get("reliability", "").strip()
    if reliability and reliability not in ("new", "reliable", "unsure", "unreliable"):
        return error("invalid reliability filter", 400)
    post_type = request.args.get("type", "").strip()
    if post_type and post_type not in VALID_POST_TYPES:
        return error("invalid post type", 400)
    gid = request.args.get("group", "").strip()
    gid_val = int(gid) if gid else None
    posts, total = get_all_posts(limit=limit, offset=offset, q=q, sort=sort,
                                 reliability=reliability, post_type=post_type,
                                 group_id=gid_val)
    return jsonify(
        data={"posts": posts, "global": {"threshold": get_threshold()}},
        meta={"total": total, "limit": limit, "offset": offset},
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok")


@app.route("/advisory/crop-calendar", methods=["GET"])
def advisory_crop_calendar():
    from datetime import date
    return jsonify(month=date.today().month, items=crop_advisory.get_crop_calendar())


@app.route("/advisory/pest-watch", methods=["GET"])
def advisory_pest_watch():
    from datetime import date
    return jsonify(month=date.today().month, items=crop_advisory.get_pest_watch())


@app.route("/advisory/seasonal", methods=["GET"])
def advisory_seasonal():
    return jsonify(crop_advisory.get_seasonal_advisory("", 50, 5.0, 30.0))


@app.route("/advisory/spray", methods=["POST"])
@limiter.limit("30 per minute")
def advisory_spray():
    payload = request.get_json(silent=True) or {}
    try:
        wind = float(payload.get("wind", 0))
        humidity = int(payload.get("humidity", 50))
        condition = str(payload.get("condition", ""))
        rain_4h = bool(payload.get("rain_4h", False))
    except (TypeError, ValueError):
        return error("wind, humidity, condition, rain_4h must be valid", 400)
    return jsonify(crop_advisory.should_spray(wind, humidity, condition, rain_4h))


@app.route("/advisory/irrigation", methods=["POST"])
@limiter.limit("30 per minute")
def advisory_irrigation():
    payload = request.get_json(silent=True) or {}
    try:
        temp = float(payload.get("temp", 30))
        condition = str(payload.get("condition", ""))
        rainfall_mm = float(payload.get("rainfall_mm", 0))
    except (TypeError, ValueError):
        return error("temp, condition, rainfall_mm must be valid", 400)

    items = []
    m = datetime.now().month
    # Dry season Jan-May, irrigate when hot + low recent rain
    if m in (1, 2, 3, 4, 5) and temp > 30 and rainfall_mm < 20:
        items.append({"severity": "orange", "text": "Dry season, high temp - irrigate if soil dry at 5 cm."})
    if m in (6, 7, 8) and rainfall_mm < 10 and temp > 32:
        items.append({"severity": "orange", "text": "Rain low, hot - irrigate paddy fields."})
    if "rain" in condition.lower() or rainfall_mm >= 20:
        items.append({"severity": "green", "text": "Rain adequate - skip irrigation."})
    return jsonify(items=items)


@app.route("/advisory/pesticide", methods=["GET"])
def advisory_pesticide():
    q = request.args.get("q", "").strip().lower()
    if not q:
        return error("q required", 400)
    res = crop_advisory.pesticide_advisory(q)
    if res is None:
        return jsonify(found=False, pesticide=None)
    return jsonify(found=True, pesticide=res)


@app.route("/market/prices", methods=["GET"])
def market_prices():
    q = request.args.get("q", "").strip()
    if q:
        return jsonify(prices=market_data.search_prices(q))
    return jsonify(prices=market_data.get_prices())


@app.route("/groups", methods=["GET"])
def list_groups():
    db = get_db()
    rows = db.execute("SELECT id, name, description, created_at FROM groups ORDER BY name ASC").fetchall()
    return jsonify(groups=[dict(id=r["id"], name=r["name"], description=r["description"], created_at=r["created_at"]) for r in rows])


@app.route("/groups/new", methods=["POST"])
@limiter.limit("10 per minute")
def create_group():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    description = str(payload.get("description", "")).strip()
    if not name or len(name) > 80:
        return error("name required, <=80 chars", 400)
    db = get_db()
    if db.execute("SELECT 1 FROM groups WHERE name = ?", (name,)).fetchone():
        return error("group already exists", 400)
    now = datetime.now(timezone.utc).isoformat()
    cur = db.execute("INSERT INTO groups (name, description, created_at) VALUES (?,?,?)", (name, description, now))
    db.commit()
    return jsonify(message="Created", group_id=cur.lastrowid), 201


@app.route("/groups/join", methods=["POST"])
@limiter.limit("30 per minute")
def join_group():
    payload = request.get_json(silent=True) or {}
    group_id = payload.get("group_id")
    user_id = str(payload.get("user_id", "")).strip() or "anonymous"
    if not group_id:
        return error("group_id required", 400)
    db = get_db()
    if db.execute("SELECT 1 FROM groups WHERE id = ?", (group_id,)).fetchone() is None:
        return error("group not found", 404)
    now = datetime.now(timezone.utc).isoformat()
    db.execute("INSERT OR IGNORE INTO group_members (group_id, user_id, role, joined_at) VALUES (?,?,?,?)",
               (group_id, user_id, "member", now))
    db.commit()
    return jsonify(message="Joined")


ALLOWED_EXT = {"jpg", "jpeg", "png", "webp"}
MAX_IMG_BYTES = 2 * 1024 * 1024


@app.route("/uploads/photo", methods=["POST"])
@limiter.limit("20 per minute")
def upload_photo():
    if "file" not in request.files:
        return error("file field required", 400)
    f = request.files["file"]
    if f.filename == "":
        return error("no file selected", 400)
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_EXT:
        return error("only jpg, jpeg, png, webp allowed", 400)
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_IMG_BYTES:
        return error("file too large (max 2MB)", 400)
    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    name = f"{uuid.uuid4().hex}.{ext}"
    f.save(os.path.join(upload_dir, name))
    return jsonify(url=f"/static/uploads/{name}"), 201


@app.route("/static/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, "static", "uploads"), filename)


@app.route("/community/<int:pid>", methods=["GET"])
def get_post(pid: int):
    db = get_db()
    row = db.execute("SELECT * FROM posts WHERE pid = ?", (pid,)).fetchone()
    if row is None:
        return error("post not found", 404)
    comments = [
        dict(id=c["id"], author=c["author"], description=c["description"],
             upvote=c["upvote"], downvote=c["downvote"], created_at=c["created_at"])
        for c in db.execute("SELECT * FROM comments WHERE pid = ? ORDER BY id ASC", (pid,))
    ]
    return jsonify(post=row_to_post(row, comments))


@app.route("/community/new", methods=["POST"])
@limiter.limit("10 per minute")
def create_post():
    payload = request.get_json(silent=True) or {}
    author = str(payload.get("author", "")).strip()
    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()
    post_type = str(payload.get("type", "general")).strip()
    image_url = payload.get("image_url")
    group_id = payload.get("group_id")

    if not author or not title or not description:
        return error("author, title and description are all required", 400)
    if len(title) > 200 or len(author) > 80 or len(description) > 2000:
        return error("field too long (title<=200, author<=80, description<=2000)", 400)
    if post_type not in VALID_POST_TYPES:
        return error("invalid post type", 400)
    if image_url and (not isinstance(image_url, str) or not image_url.startswith("/static/uploads/")):
        return error("image_url must be a valid uploaded file path", 400)
    if group_id is not None:
        if not isinstance(group_id, int):
            return error("group_id must be int", 400)
        db = get_db()
        if db.execute("SELECT 1 FROM groups WHERE id = ?", (group_id,)).fetchone() is None:
            return error("group not found", 404)

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    cur = db.execute(
        "INSERT INTO posts (author, title, description, post_type, image_url, group_id, upvote, downvote, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)",
        (author, title, description, post_type, image_url, group_id, now),
    )
    db.commit()
    pid = cur.lastrowid
    post = {
        "pid": pid,
        "author": author,
        "title": title,
        "description": description,
        "post_type": post_type,
        "image_url": image_url,
        "group_id": group_id,
        "upvote": 0,
        "downvote": 0,
        "reliability": reliability_for(0, 0),
        "created_at": now,
        "comments": [],
    }
    return jsonify(message="Created", post=post), 201


@app.route("/community/<int:pid>/vote", methods=["POST"])
@limiter.limit("30 per minute")
def vote_post(pid: int):
    payload = request.get_json(silent=True) or {}
    direction = str(payload.get("direction", "")).lower().strip()
    if direction not in ("up", "down"):
        return error('direction must be "up" or "down"', 400)

    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE pid = ?", (pid,)).fetchone()
    if post is None:
        return error("post not found", 404)

    if direction == "up":
        db.execute("UPDATE posts SET upvote = upvote + 1 WHERE pid = ?", (pid,))
    else:
        db.execute("UPDATE posts SET downvote = downvote + 1 WHERE pid = ?", (pid,))
    db.commit()
    updated = db.execute("SELECT * FROM posts WHERE pid = ?", (pid,)).fetchone()
    return jsonify(
        pid=pid,
        upvote=updated["upvote"],
        downvote=updated["downvote"],
        reliability=reliability_for(updated["upvote"], updated["downvote"]),
    )


@app.route("/community/<int:pid>/comment", methods=["POST"])
@limiter.limit("20 per minute")
def add_comment(pid: int):
    payload = request.get_json(silent=True) or {}
    author = str(payload.get("author", "")).strip()
    description = str(payload.get("description", "")).strip()
    if not author or not description:
        return error("author and description are required", 400)
    if len(author) > 80 or len(description) > 1000:
        return error("field too long (author<=80, description<=1000)", 400)

    db = get_db()
    if db.execute("SELECT 1 FROM posts WHERE pid = ?", (pid,)).fetchone() is None:
        return error("post not found", 404)

    now = datetime.now(timezone.utc).isoformat()
    cur = db.execute(
        "INSERT INTO comments (pid, author, description, upvote, downvote, created_at)"
        " VALUES (?, ?, ?, 0, 0, ?)",
        (pid, author, description, now),
    )
    db.commit()
    return jsonify(
        message="Created",
        comment={"id": cur.lastrowid, "pid": pid, "author": author,
                 "description": description, "upvote": 0, "downvote": 0,
                 "created_at": now},
    ), 201


@app.route("/community/<int:pid>", methods=["DELETE"])
@limiter.limit("10 per minute")
def delete_post(pid: int):
    db = get_db()
    if db.execute("SELECT 1 FROM posts WHERE pid = ?", (pid,)).fetchone() is None:
        return error("post not found", 404)
    db.execute("DELETE FROM comments WHERE pid = ?", (pid,))
    db.execute("DELETE FROM posts WHERE pid = ?", (pid,))
    db.commit()
    return jsonify(message="Deleted", pid=pid)


@app.errorhandler(404)
def handle_404(_e):
    return error("not found", 404)


@app.errorhandler(405)
def handle_405(_e):
    return error("method not allowed", 405)


@app.errorhandler(429)
def handle_429(_e):
    return error("rate limit exceeded, try again later", 429)


if __name__ == "__main__":
    with app.app_context():
        init_db(seed=True)
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
