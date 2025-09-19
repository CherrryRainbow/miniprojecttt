from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8000

class MyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # กัน cache ค่า sensor
        super().end_headers()

with HTTPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
