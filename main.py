import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json


def get_keys():
    keys = dict()
    with open('keys.txt') as f:
        lines = f.readlines()
        for line in lines:
            line = line.split()
            keys[line[0]] = line[1]
    return keys


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    keys = get_keys()

    def _set_headers(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _find_recommends(self, sku, rank):
        if sku not in self.keys:
            return False, {'error': 'Incorrect sku'}
        chunk_number = self.keys[sku]
        with open('chunks/' + str(chunk_number) + '.txt') as f:
            lines = f.readlines()
            recommends = None
            for line in lines:
                if line.startswith(sku):
                    recommends = line.split(',')[1:-1]
                    break
            if not recommends:
                return False, {'error': 'Incorrect sku'}
            recommends = [tuple(recommend.split()) for recommend in recommends]
            recommends = [recommend[1] for recommend in recommends if float(recommend[0]) >= rank]
            return True, recommends

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        sku = query_components['sku'][0] if 'sku' in query_components else None
        rank = query_components['rank'][0] if 'rank' in query_components else 0

        if not sku:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'sku not found'}).encode('utf-8'))
            return

        try:
            rank = float(rank)
        except ValueError:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Incorrect rank'}).encode('utf-8'))
            return

        recommends = self._find_recommends(sku, rank)
        if not recommends[0]:
            self._set_headers(400)
        else:
            self._set_headers(200)
        self.wfile.write(json.dumps(recommends[1]).encode('utf-8'))
        return


def run():
    handler_object = MyHttpRequestHandler
    PORT = 8000
    my_server = socketserver.TCPServer(("", PORT), handler_object)
    print(f'Server run on http://localhost:{PORT}')
    my_server.serve_forever()


if __name__ == '__main__':
    run()
