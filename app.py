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
        # Initialize properties and customers with billing_date
        cursor.execute('''CREATE TABLE IF NOT EXISTS properties (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT, price REAL, desc TEXT, status TEXT DEFAULT 'Available')''')
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
        # Separate path from query parameters for routing
        clean_path = self.path.split('?')[0]
        
        # API Routes - Checked first to handle data requests
        if clean_path == '/api/properties':
            self.send_json_data("SELECT * FROM properties", [])
            return
        elif clean_path == '/api/available':
            self.send_json_data("SELECT id, name FROM properties WHERE status = 'Available'", [])
            return
        elif clean_path.startswith('/api/get_property'):
            try:
                params = parse_qs(self.path.split('?')[1])
                prop_id = params.get('id', [None])[0]
                if prop_id is None:
                    self.send_error_response(400, "Missing property ID")
                    return
                self.send_json_data("SELECT * FROM properties WHERE id = ?", [prop_id])
            except Exception as e:
                self.send_error_response(400, str(e))
            return
        elif clean_path.startswith('/api/get_rental_details'):
            try:
                params = parse_qs(self.path.split('?')[1])
                cust_id = params.get('id', [None])[0]
                if cust_id is None:
                    self.send_error_response(400, "Missing customer ID")
                    return
                query = '''SELECT c.name, c.contact, p.name, p.price, p.desc, p.status, c.billing_date 
                           FROM customers c 
                           JOIN properties p ON c.property_id = p.id 
                           WHERE c.id = ?'''
                self.send_json_data(query, [cust_id])
            except Exception as e:
                self.send_error_response(400, str(e))
            return
        elif clean_path == '/api/report':
            query = '''SELECT p.name, c.contact, p.price, c.name, c.billing_date, c.id 
                       FROM properties p JOIN customers c ON p.id = c.property_id'''
            self.send_json_data(query, [])
            return

        # HTML Routing - Ensures .html?id=1 maps to the file correctly
        if clean_path == '/': 
            self.path = '/templates/index.html'
        elif clean_path.endswith('.html'): 
            self.path = f'/templates{clean_path}'
        
        return super().do_GET()

    def send_json_data(self, query, params):
        """Execute query with parameterized statements and return JSON"""
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall()
            conn.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(json.dumps(data).encode())))
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_error_response(500, f"Database error: {str(e)}")

    def send_error_response(self, code, message):
        """Send a JSON error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        error_data = json.dumps({"error": message}).encode()
        self.send_header('Content-Length', str(len(error_data)))
        self.end_headers()
        self.wfile.write(error_data)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, "Invalid request")
                return
                
            post_data = parse_qs(self.rfile.read(content_length).decode('utf-8'))
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            if self.path == '/add_property':
                name = post_data.get('name', [None])[0]
                price = post_data.get('price', [None])[0]
                desc = post_data.get('desc', [''])[0]
                
                if not name or not price:
                    conn.close()
                    self.send_error_response(400, "Missing required fields")
                    return
                
                try:
                    price = float(price)
                except ValueError:
                    conn.close()
                    self.send_error_response(400, "Invalid price format")
                    return
                
                cursor.execute("INSERT INTO properties (name, price, desc) VALUES (?, ?, ?)",
                               (name, price, desc))
                               
            elif self.path == '/update_property':
                prop_id = post_data.get('id', [None])[0]
                name = post_data.get('name', [None])[0]
                price = post_data.get('price', [None])[0]
                desc = post_data.get('desc', [''])[0]
                
                if not prop_id or not name or not price:
                    conn.close()
                    self.send_error_response(400, "Missing required fields")
                    return
                
                try:
                    price = float(price)
                    prop_id = int(prop_id)
                except ValueError:
                    conn.close()
                    self.send_error_response(400, "Invalid data format")
                    return
                
                cursor.execute("UPDATE properties SET name=?, price=?, desc=? WHERE id=?",
                               (name, price, desc, prop_id))
                               
            elif self.path == '/delete_property':
                prop_id = post_data.get('id', [None])[0]
                
                if not prop_id:
                    conn.close()
                    self.send_error_response(400, "Missing property ID")
                    return
                
                try:
                    prop_id = int(prop_id)
                except ValueError:
                    conn.close()
                    self.send_error_response(400, "Invalid property ID")
                    return
                
                cursor.execute("DELETE FROM customers WHERE property_id = ?", (prop_id,))
                cursor.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
                
            elif self.path == '/add_customer':
                cname = post_data.get('cname', [None])[0]
                contact = post_data.get('contact', [None])[0]
                billing_date = post_data.get('billing_date', [None])[0]
                prop_id = post_data.get('property_id', [None])[0]
                
                if not all([cname, contact, billing_date, prop_id]):
                    conn.close()
                    self.send_error_response(400, "Missing required fields")
                    return
                
                try:
                    prop_id = int(prop_id)
                except ValueError:
                    conn.close()
                    self.send_error_response(400, "Invalid property ID")
                    return
                
                cursor.execute("INSERT INTO customers (name, contact, billing_date, property_id) VALUES (?, ?, ?, ?)",
                               (cname, contact, billing_date, prop_id))
                cursor.execute("UPDATE properties SET status = 'Rented' WHERE id = ?", (prop_id,))

            conn.commit()
            conn.close()
            self.send_response(303)
            self.send_header('Location', '/property_list.html')
            self.send_header('Content-Length', '0')
            self.end_headers()
            
        except Exception as e:
            self.send_error_response(500, f"Server error: {str(e)}")

if __name__ == "__main__":
    init_db()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RentalHandler) as httpd:
        print(f"✅ Server running at http://localhost:{PORT}")
        httpd.serve_forever()