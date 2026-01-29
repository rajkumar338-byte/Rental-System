import http.server
import socketserver
import sqlite3
import json
import sys
from urllib.parse import parse_qs
from datetime import datetime

PORT = 8000

def init_db():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS properties (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT, price REAL, desc TEXT, status TEXT DEFAULT 'Available')''')
        # ADDED: billing_date column
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT, contact TEXT, billing_date TEXT, property_id INTEGER,
                            FOREIGN KEY(property_id) REFERENCES properties(id))''')
        conn.commit()
        conn.close()
        print("Database Connected Successfully")
    except Exception as e:
        print(f"Database Error: {e}")
        sys.exit(1)

class RentalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        clean_path = self.path.split('?')[0]
        
        if clean_path == '/api/properties':
            self.send_json_data("SELECT * FROM properties")
            return
        elif clean_path == '/api/available':
            self.send_json_data("SELECT id, name FROM properties WHERE status = 'Available'")
            return
        elif clean_path == '/api/get_property':
            params = parse_qs(self.path.split('?')[1])
            self.send_json_data(f"SELECT * FROM properties WHERE id = {params['id'][0]}")
            return
        elif clean_path == '/api/get_rental_details':
            params = parse_qs(self.path.split('?')[1])
            # FETCHED: billing_date in the join
            query = f'''SELECT c.name, c.contact, p.name, p.price, p.desc, p.status, c.billing_date 
                       FROM customers c 
                       JOIN properties p ON c.property_id = p.id 
                       WHERE c.id = {params['id'][0]}'''
            self.send_json_data(query)
            return
        elif clean_path == '/api/report':
            # UPDATED: Added billing_date to report list
            query = '''SELECT p.name, c.contact, p.price, c.name, c.billing_date, c.id 
                       FROM properties p JOIN customers c ON p.id = c.property_id'''
            self.send_json_data(query)
            return

        if clean_path == '/': self.path = '/templates/index.html'
        elif clean_path.endswith('.html'): self.path = f'/templates{clean_path}'
        return super().do_GET()

    def send_json_data(self, query):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = parse_qs(self.rfile.read(content_length).decode('utf-8'))
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        if self.path == '/add_property':
            cursor.execute("INSERT INTO properties (name, price, desc) VALUES (?, ?, ?)",
                           (post_data['name'][0], post_data['price'][0], post_data['desc'][0]))
        elif self.path == '/update_property':
            cursor.execute("UPDATE properties SET name=?, price=?, desc=? WHERE id=?",
                           (post_data['name'][0], post_data['price'][0], post_data['desc'][0], post_data['id'][0]))
        elif self.path == '/delete_property':
            # NEW: Delete property logic
            p_id = post_data['id'][0]
            cursor.execute("DELETE FROM customers WHERE property_id = ?", (p_id,))
            cursor.execute("DELETE FROM properties WHERE id = ?", (p_id,))
        elif self.path == '/add_customer':
            p_id = post_data['property_id'][0]
            # AUTOMATIC: Sets current date as billing date
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO customers (name, contact, billing_date, property_id) VALUES (?, ?, ?, ?)",
                           (post_data['cname'][0], post_data['contact'][0], today, p_id))
            cursor.execute("UPDATE properties SET status = 'Rented' WHERE id = ?", (p_id,))

        conn.commit()
        conn.close()
        self.send_response(303)
        self.send_header('Location', '/property_list.html')
        self.end_headers()

if __name__ == "__main__":
    init_db()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RentalHandler) as httpd:
        print(f"✅ Server running at http://localhost:{PORT}")
        httpd.serve_forever()