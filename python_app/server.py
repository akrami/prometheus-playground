import http.server
import random
import time
from prometheus_client import start_http_server, Counter, Gauge, Summary, Histogram

REQUESTS = Counter('http_requests_total', 'Total requests to the HTTP server')
EXCEPTIONS = Counter('http_exceptions_total', 'Total number of exceptions')

INPROGRESS = Gauge('http_requests_inprogress', 'Total number of HTTP requests processing')
LASTCALL = Gauge('http_requests_last_call', 'Last HTTP request timestamp')

LATENCY = Summary('http_latency_seconds', 'Time for a request')

SIZE = Histogram('http_response_size', 'Size of the response', buckets=[2**x for x in range(0, 10)])

class MyHandler(http.server.BaseHTTPRequestHandler):
    @EXCEPTIONS.count_exceptions()
    @INPROGRESS.track_inprogress()
    @LATENCY.time()
    def do_GET(self):
        response = b''
        REQUESTS.inc()
        if(self.path.lower() == '/faulty'):
            if random.random() < 0.2:
                raise Exception
            response = b'this could be faulty'
        if(self.path.lower() == '/job'):
            import job
            response = b'job executed'
        else:
            response = b'this is main'
        self.send_response(200)
        self.end_headers()
        self.wfile.write(response)
        SIZE.observe(len(response))
        LASTCALL.set(time.time())

if __name__ == "__main__":
    start_http_server(8000)
    server = http.server.HTTPServer(('0.0.0.0', 8001), MyHandler)
    server.serve_forever()
