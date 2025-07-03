import http.server
import socketserver
import os

class HTTP11RequestHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

HLS_DIRECTORY ="/home/maria/mi_proyecto/hls"
os.chdir(HLS_DIRECTORY)

PORT = 8080

with socketserver.TCPServer(("", PORT), HTTP11RequestHandler) as httpd:
    print(f"Servidor HTTP/1.1 sirviendo desde {HLS_DIRECTORY} en puerto {PORT}")
    httpd.serve_forever()
