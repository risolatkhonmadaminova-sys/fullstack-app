from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@app.before_request
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            content TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return "Backend is running!"

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, content FROM items')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([{"id": r[0], "content": r[1]} for r in rows])

@app.route('/api/data', methods=['POST'])
def add_data():
    content = request.json.get('content')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO items (content) VALUES (%s)', (content,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "added"})

@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM items WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "deleted"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
