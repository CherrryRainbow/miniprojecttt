from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import requests
import flet as ft
from threading import Thread
from time import sleep

class SimpleHandlerIndex(BaseHTTPRequestHandler):
    humid = temp = soil = "-"
    pump = "OFF"
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    # GET request
    def do_GET(self):
        if self.path == "/":
            self._set_headers(content_type="text/html")
            self.wfile.write("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Embedded System Mini Project</title>
                    <style>
                        body, html {
                        margin: 0;
                        padding: 0;
                        height: 100%;
                    }
                    </style>
                </head>
                <body>
                    <iframe src="http://127.0.0.1:5500/" allowfullscreen style="width:100%;height:100%;"></iframe>
                </body>
                </html>
                """.encode())
            
        else:
            self._set_headers(status=404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('UTF-8'))
        self.transfer_frontend()
    # POST request
    def do_POST(self):
        if self.path == "/device":
            content_length = int(self.headers.get('Content-Length', 0))
            body_device = self.rfile.read(content_length)
            try:
                data:dict = json.loads(body_device)
                self.humid = data.get('humid','-')
                self.temp = data.get("temp",'-')
                self.soil = data.get("soil",'-')
            except:
                data = {"error": "Invalid JSON"}
            response = {
                "pswd":"ccc",
                "pump":self.pump
            }
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
        
    def transfer_frontend(self):
        while True:
            # content_length = int(self.headers.get('Content-Length', 0))
            body_flet = requests.post("http://127.0.0.1:5500" if not ON_PRODUCT else "https://cherry-miniproject.onrender.com:5500/")
            try:
                data:dict = json.loads(body_flet)
                self.pump = data.get('pump','OFF')
            except:
                data = {"error": "Invalid JSON"}
                response = {
                "pswd":"ccc",
                "submit":"server",
                "pump":self.pump,
                "humid":self.humid,
                "temp":self.temp,
                "soil":self.soil
            }
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())

LOCAL_HOST = "http://127.0.0.1:8000"
PRODUCTION_HOST = "https://cherry-miniproject.onrender.com:8000"

ON_PRODUCT = False

def frontend(page:ft.Page):
    global pump_status
    pump_status = "OFF"
    def csrf_res():
        global pump_status
        while True:
            data = {
                "pswd":"ccc",
                "submit":"pump",
                "pump":pump_status,
            }
            try:
                data_json:dict = json.loads(
                    requests.post(
                        url=PRODUCTION_HOST if ON_PRODUCT else LOCAL_HOST,
                        data=data
                    ).text
                )
                humid_text.value = f'{data_json.get("humid",humid_text.value)}'
                temp_text.value = f'{data_json.get("temp",temp_text.value)}'
                soil_text.value = f'{data_json.get("soil",soil_text.value)}'
                pump_text.value = f'{data_json.get("pump",pump_text.value)}'
                err_text.value = "No Error"
                
            except Exception as err:
                err_text.value = f"{err}"
            page.update()
            sleep(1)
    
    def change_pump_status(e,val):
        global pump_status
        pump_status = val
    
    pump_sw_on = ft.TextButton(text="ON",on_click=lambda e:change_pump_status(e,"ON"))
    pump_sw_off = ft.TextButton(text="OFF",on_click=lambda e:change_pump_status(e,"OFF"))
    
    [pump_text, humid_text, temp_text, soil_text] = [ft.Text("-") for i in range(4)]
    err_text = ft.Text("No Error")
    
    status_table = ft.DataTable(
        columns=[
            ft.DataColumn(
                label=ft.Text("Variable"),
            ),
            ft.DataColumn(
                label=ft.Text("Value"),
            )
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(
                    content=ft.Text("air humidity: ")
                    ),
                    ft.DataCell(
                        content=humid_text
                    )
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        content=ft.Text("air temperature: ")
                    ),
                    ft.DataCell(
                        content=temp_text
                    )
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        content=ft.Text("soil humidity: ")
                    ),
                    ft.DataCell(
                        content=soil_text
                    )
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(    
                        content=ft.Text("pump status: ")
                    ),
                    ft.DataCell(
                        content=pump_text
                    )
                ]
            ),
        ]
    )
    thread_res = Thread(target=csrf_res,daemon=True)
    thread_res.start()
    page.add(
        ft.Text("pump switch"),
        ft.Row(
            [
                pump_sw_on,
                pump_sw_off
            ]
        ),
        status_table,
        err_text
    )

def run_http():
    server_index = ThreadingHTTPServer(("127.0.0.1", 8000), SimpleHandlerIndex)
    print(f"HTTP server running on http://127.0.0.1:8000")
    server_index.serve_forever()

run_http()
ft.app(frontend,port=5500,view=ft.AppView.WEB_BROWSER)
