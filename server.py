from http.server import BaseHTTPRequestHandler, HTTPServer
import json

sensor_data = {"temperature": None, "humidity": None, "soil": None}
pump_status = {"status": "off"}

class MyHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/latest":
            self._set_headers()
            self.wfile.write(json.dumps(sensor_data).encode())
        elif self.path == "/pump_status":
            self._set_headers()
            self.wfile.write(json.dumps(pump_status).encode())
        elif self.path == "/":
            self._set_headers(200, "text/html")
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
        else:
            self._set_headers(404)
            self.wfile.write(b"Not found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except:
            self._set_headers(400)
            self.wfile.write(b"Invalid JSON")
            return

        if self.path == "/data":
            sensor_data.update(data)
            self._set_headers()
            self.wfile.write(b"Data received")
        elif self.path == "/pump":
            pump_status.update(data)
            self._set_headers()
            self.wfile.write(b"Pump updated")
        else:
            self._set_headers(404)
            self.wfile.write(b"Not found")

def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    server = server_class(("", port), handler_class)
    print(f"Server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run()

