import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "canteen")
DB_USER = os.getenv("POSTGRES_USER", "canteen_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "canteen_password")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT
    )

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "canteen-backend"})

@app.get("/api/menu")
def menu():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, description, price FROM menu_items ORDER BY id")
            return jsonify(cur.fetchall())

@app.post("/api/orders")
def create_order():
    data = request.get_json() or {}
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            total = 0
            checked = []

            for item in items:
                cur.execute(
                    "SELECT id, name, price FROM menu_items WHERE id = %s",
                    (item["menu_item_id"],)
                )
                menu_item = cur.fetchone()
                quantity = int(item.get("quantity", 0))

                if not menu_item or quantity <= 0:
                    return jsonify({"error": "Invalid cart item"}), 400

                total += float(menu_item["price"]) * quantity
                checked.append((menu_item, quantity))

            cur.execute(
                "INSERT INTO orders (status, total) VALUES ('PLACED', %s) RETURNING id",
                (total,)
            )
            order_id = cur.fetchone()["id"]

            for menu_item, quantity in checked:
                cur.execute(
                    """INSERT INTO order_items
                       (order_id, menu_item_id, item_name, quantity, price)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (order_id, menu_item["id"], menu_item["name"],
                     quantity, menu_item["price"])
                )

            conn.commit()

    return jsonify({
        "message": "Order placed successfully",
        "order_id": order_id,
        "status": "PLACED",
        "total": total
    }), 201

@app.get("/api/orders")
def orders():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, status, total, created_at
                FROM orders
                ORDER BY id DESC
            """)
            orders_data = cur.fetchall()

            for order in orders_data:
                cur.execute("""
                    SELECT item_name AS name, quantity, price
                    FROM order_items
                    WHERE order_id = %s
                    ORDER BY id
                """, (order["id"],))
                order["items"] = cur.fetchall()

            return jsonify(orders_data)

@app.get("/api/orders/<int:order_id>")
def get_order(order_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, status, total, created_at FROM orders WHERE id = %s",
                (order_id,)
            )
            order = cur.fetchone()

            if not order:
                return jsonify({"error": "Order not found"}), 404

            cur.execute("""
                SELECT item_name AS name, quantity, price
                FROM order_items
                WHERE order_id = %s
                ORDER BY id
            """, (order_id,))
            order["items"] = cur.fetchall()
            return jsonify(order)

@app.patch("/api/orders/<int:order_id>/status")
def update_status(order_id):
    data = request.get_json() or {}
    status = str(data.get("status", "")).upper()
    allowed = ["PLACED", "PREPARING", "READY", "COMPLETED", "CANCELLED"]

    if status not in allowed:
        return jsonify({"error": "Invalid status"}), 400

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE orders SET status = %s WHERE id = %s RETURNING id, status",
                (status, order_id)
            )
            result = cur.fetchone()

            if not result:
                return jsonify({"error": "Order not found"}), 404

            conn.commit()
            return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
