import http.server
import random
from prometheus_client import start_http_server, Counter

REQUESTS = Counter('http_requests_total', 'Total requests to the HTTP server')
EXCEPTIONS = Counter('http_exceptions_total', 'Total number of exceptions')

class MyHandler(http.server.BaseHTTPRequestHandler):
    @EXCEPTIONS.count_exceptions()
    def do_GET(self):
        REQUESTS.inc()
        if(self.path.lower() == '/faulty'):
            if random.random() < 0.2:
                raise Exception
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'this could be faulty')
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'this is main')

if __name__ == "__main__":
    start_http_server(8000)
    server = http.server.HTTPServer(('0.0.0.0', 8001), MyHandler)
    server.serve_forever()