import http.server
import socketserver
import sqlite3
import json
import sys
from urllib.parse import parse_qs

PORT = 8000

def init_db():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS properties (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT, price REAL, desc TEXT, status TEXT DEFAULT 'Available')''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT, contact TEXT, property_id INTEGER,
                            FOREIGN KEY(property_id) REFERENCES properties(id))''')
        conn.commit()
        conn.close()
        print("Database Connected Successfully")
    except Exception as e:
        print(f"Database Error: {e}")
        sys.exit(1)

class RentalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # FIX: Strip query parameters to find the correct HTML file in templates
        clean_path = self.path.split('?')[0]
        
        if clean_path == '/': 
            self.path = '/templates/index.html'
        elif clean_path.endswith('.html'): 
            self.path = f'/templates{clean_path}'
        
        # API Routes
        if self.path == '/api/properties':
            self.send_json_data("SELECT * FROM properties")
        elif self.path == '/api/available':
            self.send_json_data("SELECT id, name FROM properties WHERE status = 'Available'")
        elif self.path.startswith('/api/get_property'):
            params = parse_qs(self.path.split('?')[1])
            self.send_json_data(f"SELECT * FROM properties WHERE id = {params['id'][0]}")
        elif self.path == '/api/report':
            # FIX: Ensure customer ID is included in the SELECT for the View action
            query = '''SELECT p.name, c.contact, p.price, c.name, c.id 
                       FROM properties p JOIN customers c ON p.id = c.property_id'''
            self.send_json_data(query)
        else:
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
        elif self.path == '/add_customer':
            p_id = post_data['property_id'][0]
            cursor.execute("INSERT INTO customers (name, contact, property_id) VALUES (?, ?, ?)",
                           (post_data['cname'][0], post_data['contact'][0], p_id))
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