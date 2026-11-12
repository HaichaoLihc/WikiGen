"""Browse the generated wikis in a browser:  python -m wikigen.serve out --port 8766"""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VIEWER = Path(__file__).with_name("viewer.html")


class Handler(SimpleHTTPRequestHandler):
    """Serves the viewer page, the list of wikis, and the files of the output folder as they are."""

    def do_GET(self):
        if self.path == "/":
            self.reply(VIEWER.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/wikis.json":
            names = sorted(toc.parent.name for toc in Path(self.directory).glob("*/toc.json"))
            self.reply(json.dumps(names).encode(), "application/json")
        else:
            super().do_GET()

    def reply(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", help="folder that holds one sub-folder per generated wiki")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    print(f"http://localhost:{args.port}")
    ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=args.out)).serve_forever()
