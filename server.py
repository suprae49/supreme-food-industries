#!/usr/bin/env python3
"""Supreme Food Industry — unified demo backend (serves site + API)."""

from __future__ import annotations

import json
import math
import os
import re
import secrets
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

ROOT = Path(__file__).resolve().parent
# Vercel has a read-only filesystem except /tmp — use /tmp for SQLite there
if os.environ.get("VERCEL"):
    DATA_DIR = Path("/tmp/sfi-data")
else:
    DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "sfi.db"
BIN_DIR = ROOT / "bin"
PRICE_PER_KG_NPR = 110
sys.path.insert(0, str(ROOT / "polyglot" / "python"))
try:
    from rice_calc import calc_bags  # noqa: E402
except ImportError:
    def calc_bags(bags: int, kg_per_bag: float = 25.0) -> dict:
        total = bags * kg_per_bag
        return {
            "ok": True,
            "lang": "python",
            "bags": bags,
            "kg_per_bag": kg_per_bag,
            "total_kg": round(total, 2),
            "total_quintal": round(total / 100.0, 3),
            "csr_fund_npr": bags * 25,
        }

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
app.secret_key = os.environ.get("SFI_SECRET", "supreme-food-industry-demo-secret")

ADMIN_PHONES = {"9841043864", "9840067681"}
ADMIN_PASSWORD = os.environ.get("SFI_ADMIN_PASSWORD", "supreme@2000@")
ADMIN_NAMES = {
    "9841043864": "Supreme Admin",
    "9840067681": "Supreme Admin 2",
}

COMPANY = {
    "brand_ne": "सुप्रिम खाद्य उद्योग",
    "brand_en": "Supreme Food Industry",
    "brand_mark": "सुप्रिम ब्राण्ड",
    "tagline": "100% Local Product",
    "product_ne": "लोकल पोखरेली चामल",
    "product_en": "Local Pokhareli Rice",
    "weight": "२५ के.जी. (भर्ने बेलामा)",
    "weight_en": "25 KG (at packing)",
    "price_per_kg_npr": PRICE_PER_KG_NPR,
    "price_per_bag_npr": 25 * PRICE_PER_KG_NPR,
    "shelf_life": "Best Before 6 Months",
    "producer_ne": "उत्पादक: सुप्रिम खाद्य उद्योग",
    "address_ne": "पञ्चकन्या गा. पा.-२, नुवाकोट",
    "address_en": "Panchakanya Rural Municipality-2, Nuwakot, Nepal",
    "mobiles": [
        {
            "number": "9841043864",
            "display_ne": "९८४१०४३८६४",
            "tel": "+9779841043864",
            "whatsapp": "https://wa.me/9779841043864",
            "label": "Primary",
        },
        {
            "number": "9840067681",
            "display_ne": "९८४००६७६८१",
            "tel": "+9779840067681",
            "whatsapp": "https://wa.me/9779840067681",
            "label": "Secondary",
        },
    ],
    "pack_fields": ["Batch No", "Mfg Date", "M.R.P (Incl of all taxes)", "Best Before 6 Months"],
    "project_ne": "प्रधानमन्त्री कृषि आधुनिकीकरण परियोजना",
    "project_unit_ne": "परियोजना कार्यान्वयन एकाइ नुवाकोटद्वारा प्रवर्द्धित",
    "store_ne": "सुप्रिम खाद्य भण्डार",
    "varieties": [
        {"name_ne": "लोकल पोखरेली", "name_en": "Local Pokhareli", "pack": "25 KG"},
        {"name_ne": "ब्राउन १", "name_en": "Brown 1", "pack": "25 KG"},
        {"name_ne": "ब्राउन २", "name_en": "Brown 2", "pack": "25 KG"},
    ],
    "gallery": [
        {"src": "assets/facebook/photo1.jpg", "caption": "सुप्रिम ब्राण्ड · लोकल पोखरेली"},
        {"src": "assets/facebook/product_1.jpg", "caption": "गोदामका बोराहरू"},
        {"src": "assets/rice/field.jpg", "caption": "धान खेत"},
        {"src": "assets/rice/grains.jpg", "caption": "चामल दाना"},
        {"src": "assets/rice/harvest.jpg", "caption": "कटानी"},
        {"src": "assets/rice/paddy.jpg", "caption": "प्याडी"},
        {"src": "assets/rice/raw.jpg", "caption": "कच्चा चामल"},
        {"src": "assets/rice/cook.jpg", "caption": "पकाएको चामल"},
        {"src": "assets/rice/bowl.jpg", "caption": "भात"},
        {"src": "assets/rice/plated.jpg", "caption": "थालको चामल"},
        {"src": "assets/rice/plant.jpg", "caption": "धान बाली"},
    ],
    "csr": {
        "title_ne": "नयाँ वर्ष २०८३ · सामाजिक उत्तरदायित्व",
        "body_ne": (
            "प्रत्येक बोराको बिक्रीमा प्रति के.जी. रू. १ का दरले रू. २५ "
            "सामाजिक उत्तरदायित्व कोषमा जम्मा हुन्छ।"
        ),
    },
}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: object) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                message TEXT,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                variety TEXT NOT NULL,
                bags INTEGER NOT NULL,
                total_kg REAL NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        cols = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "is_admin" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        # Keep historical orders unpriced; the original app never stored a sale price.
        order_cols = {row[1] for row in conn.execute("PRAGMA table_info(orders)").fetchall()}
        for column in ("price_per_kg_npr", "total_price_npr"):
            if column not in order_cols:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {column} REAL")
        seed_admins(conn)
        conn.commit()


def seed_admins(conn: sqlite3.Connection) -> None:
    password_hash = generate_password_hash(ADMIN_PASSWORD)
    for phone in ADMIN_PHONES:
        existing = conn.execute(
            "SELECT id FROM users WHERE phone = ?", (phone,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE users SET password_hash = ?, is_admin = 1, name = ? WHERE phone = ?",
                (password_hash, ADMIN_NAMES.get(phone, "Supreme Admin"), phone),
            )
        else:
            conn.execute(
                """
                INSERT INTO users (name, phone, password_hash, is_admin, created_at)
                VALUES (?, ?, ?, 1, ?)
                """,
                (ADMIN_NAMES.get(phone, "Supreme Admin"), phone, password_hash, now_iso()),
            )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("977") and len(digits) > 10:
        digits = digits[3:]
    return digits


def public_user(row: sqlite3.Row | dict) -> dict:
    is_admin = bool(row["is_admin"]) if "is_admin" in row.keys() else row["phone"] in ADMIN_PHONES
    return {
        "id": row["id"],
        "name": row["name"],
        "phone": row["phone"],
        "is_admin": is_admin,
    }


def issue_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db = get_db()
    db.execute(
        "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
        (token, user_id, now_iso()),
    )
    db.commit()
    return token


def current_user():
    auth = request.headers.get("Authorization", "")
    token = auth[7:].strip() if auth.startswith("Bearer ") else ""
    if not token:
        return None
    return get_db().execute(
        """
        SELECT users.id, users.name, users.phone, users.is_admin
        FROM sessions JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"ok": False, "error": "लगइन आवश्यक छ।"}), 401
        if not user["is_admin"] and user["phone"] not in ADMIN_PHONES:
            return jsonify({"ok": False, "error": "एडमिन अनुमति छैन।"}), 403
        return fn(*args, **kwargs)

    return wrapper


def require_json(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({"ok": False, "error": "JSON body required."}), 400
        return fn(*args, **kwargs)

    return wrapper


def run_native_calc(bags: int, kg_per_bag: float) -> dict | None:
    for name in ("rice_calc_cpp", "rice_calc_c"):
        binary = BIN_DIR / name
        if not binary.exists():
            continue
        try:
            proc = subprocess.run(
                [str(binary), str(bags), str(kg_per_bag)],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout.strip())
                data["csr_fund_npr"] = bags * 25
                return data
        except Exception:
            continue
    return None


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "supreme-food-industry", "stack": ["html", "css", "js", "python", "c", "cpp", "php", "java"]})


@app.get("/api/company")
def company():
    return jsonify({"ok": True, "company": COMPANY})


@app.get("/api/calc")
def calc():
    try:
        bags = int(request.args.get("bags", "1"))
        kg = float(request.args.get("kg", "25"))
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid bags/kg"}), 400
    if bags < 0 or bags > 100000 or not math.isfinite(kg) or kg <= 0:
        return jsonify({"ok": False, "error": "Out of range"}), 400

    # Add sale pricing here so existing C/C++ binaries and Python agree.
    result = run_native_calc(bags, kg) or calc_bags(bags, kg)
    result["price_per_kg_npr"] = PRICE_PER_KG_NPR
    result["total_price_npr"] = round(bags * kg * PRICE_PER_KG_NPR, 2)
    return jsonify(result)


@app.post("/api/signup")
@require_json
def signup():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    phone = normalize_phone(str(data.get("phone", "")))
    password = str(data.get("password", ""))

    if len(name) < 2:
        return jsonify({"ok": False, "error": "कृपया पूरा नाम लेख्नुहोस्।"}), 400
    if len(phone) < 10:
        return jsonify({"ok": False, "error": "मान्य मोबाइल नम्बर दिनुहोस्।"}), 400
    if len(password) < 4:
        return jsonify({"ok": False, "error": "पासवर्ड कम्तीमा ४ अक्षरको हुनुपर्छ।"}), 400

    db = get_db()
    if phone in ADMIN_PHONES:
        return jsonify({"ok": False, "error": "यो नम्बर एडमिनका लागि सुरक्षित छ। लगइन गर्नुहोस्।"}), 403
    if db.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone():
        return jsonify({"ok": False, "error": "यो नम्बर पहिले नै दर्ता छ। लगइन गर्नुहोस्।"}), 409

    cur = db.execute(
        "INSERT INTO users (name, phone, password_hash, is_admin, created_at) VALUES (?, ?, ?, 0, ?)",
        (name, phone, generate_password_hash(password), now_iso()),
    )
    db.commit()
    user = {"id": cur.lastrowid, "name": name, "phone": phone, "is_admin": False}
    return jsonify({"ok": True, "user": user, "token": issue_token(user["id"])})


@app.post("/api/login")
@require_json
def login():
    data = request.get_json(silent=True) or {}
    phone = normalize_phone(str(data.get("phone", "")))
    password = str(data.get("password", ""))
    row = get_db().execute(
        "SELECT id, name, phone, password_hash, is_admin FROM users WHERE phone = ?",
        (phone,),
    ).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"ok": False, "error": "मोबाइल वा पासवर्ड मिलेन।"}), 401
    user = public_user(row)
    return jsonify({"ok": True, "user": user, "token": issue_token(user["id"])})


@app.post("/api/logout")
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth[7:].strip() if auth.startswith("Bearer ") else ""
    if token:
        db = get_db()
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        db.commit()
    return jsonify({"ok": True})


@app.get("/api/me")
def me():
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "लगइन आवश्यक छ।"}), 401
    return jsonify({"ok": True, "user": public_user(user)})


@app.get("/api/admin/orders")
@require_admin
def admin_orders():
    rows = get_db().execute(
        """
        SELECT id, name, phone, variety, bags, total_kg, price_per_kg_npr, total_price_npr, note, created_at
        FROM orders
        ORDER BY id DESC
        LIMIT 500
        """
    ).fetchall()
    return jsonify({"ok": True, "orders": [dict(r) for r in rows]})


@app.get("/api/admin/inquiries")
@require_admin
def admin_inquiries():
    rows = get_db().execute(
        "SELECT id, name, phone, message, created_at FROM inquiries ORDER BY id DESC LIMIT 500"
    ).fetchall()
    return jsonify({"ok": True, "inquiries": [dict(r) for r in rows]})


@app.get("/api/admin/stats")
@require_admin
def admin_stats():
    db = get_db()
    orders = db.execute("SELECT COUNT(*) AS c, COALESCE(SUM(bags),0) AS bags, COALESCE(SUM(total_kg),0) AS kg FROM orders").fetchone()
    inquiries = db.execute("SELECT COUNT(*) AS c FROM inquiries").fetchone()
    users = db.execute("SELECT COUNT(*) AS c FROM users WHERE is_admin = 0").fetchone()
    return jsonify(
        {
            "ok": True,
            "stats": {
                "orders": orders["c"],
                "bags": orders["bags"],
                "total_kg": orders["kg"],
                "inquiries": inquiries["c"],
                "customers": users["c"],
            },
        }
    )


@app.post("/api/contact")
@require_json
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    phone = normalize_phone(str(data.get("phone", "")))
    message = str(data.get("message", "")).strip()
    if len(name) < 2:
        return jsonify({"ok": False, "error": "कृपया नाम लेख्नुहोस्।"}), 400
    if len(phone) < 10:
        return jsonify({"ok": False, "error": "मान्य मोबाइल नम्बर दिनुहोस्।"}), 400

    user = current_user()
    db = get_db()
    cur = db.execute(
        "INSERT INTO inquiries (name, phone, message, user_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, phone, message, user["id"] if user else None, now_iso()),
    )
    db.commit()
    return jsonify(
        {
            "ok": True,
            "inquiry_id": cur.lastrowid,
            "message": "धन्यवाद — सन्देश सेभ भयो। हामी छिट्टै सम्पर्क गर्नेछौं।",
            "company_mobiles": [m["number"] for m in COMPANY["mobiles"]],
        }
    )


@app.post("/api/order")
@require_json
def order():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    phone = normalize_phone(str(data.get("phone", "")))
    variety = str(data.get("variety", "Local Pokhareli")).strip() or "Local Pokhareli"
    note = str(data.get("note", "")).strip()
    try:
        bags = int(data.get("bags", 1))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "बोरा संख्या गलत छ।"}), 400
    if len(name) < 2 or len(phone) < 10 or bags < 1 or bags > 5000:
        return jsonify({"ok": False, "error": "अर्डर विवरण जाँच गर्नुहोस्।"}), 400

    total_kg = bags * 25.0
    total_price_npr = total_kg * PRICE_PER_KG_NPR
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO orders (name, phone, variety, bags, total_kg, price_per_kg_npr, total_price_npr, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, phone, variety, bags, total_kg, PRICE_PER_KG_NPR, total_price_npr, note, now_iso()),
    )
    db.commit()
    return jsonify(
        {
            "ok": True,
            "order_id": cur.lastrowid,
            "bags": bags,
            "total_kg": total_kg,
            "price_per_kg_npr": PRICE_PER_KG_NPR,
            "total_price_npr": total_price_npr,
            "csr_fund_npr": bags * 25,
            "message": f"अर्डर #{cur.lastrowid} सेभ भयो · {bags} बोरा · {int(total_kg)} के.जी. · कुल रू. {total_price_npr:,.0f}",
            "call": COMPANY["mobiles"][0]["tel"],
        }
    )


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.get("/<path:path>")
def static_proxy(path: str):
    target = ROOT / path
    if target.is_file():
        return send_from_directory(ROOT, path)
    return send_from_directory(ROOT, "index.html")


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5173"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")

