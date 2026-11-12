"""Browse the generated wikis in a browser:  python -m wikigen.serve out --port 8766
Or write them as a static site, e.g. for GitHub Pages:  python -m wikigen.serve out --export site"""
import argparse
import json
import shutil
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


def export(out, site):
    """Write the viewer and every wiki under `out` as static files that any web host can serve."""
    names = sorted(toc.parent.name for toc in out.glob("*/toc.json"))
    site.mkdir(parents=True, exist_ok=True)
    shutil.copy(VIEWER, site / "index.html")
    (site / ".nojekyll").write_text("")  # stops GitHub Pages from converting the .md pages to HTML
    (site / "wikis.json").write_text(json.dumps(names))
    for name in names:
        (site / name).mkdir(exist_ok=True)
        toc = json.loads((out / name / "toc.json").read_text())
        toc.pop("planner_session", None)  # an internal conversation id, of no use to readers
        (site / name / "toc.json").write_text(json.dumps(toc, indent=1))
        for page in (out / name).glob("*.md"):
            shutil.copy(page, site / name / page.name)
    return names


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", help="folder that holds one sub-folder per generated wiki")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--export", type=Path, help="write a static site to this folder instead of serving")
    args = parser.parse_args()
    if args.export:
        print("exported:", ", ".join(export(Path(args.out), args.export)))
        raise SystemExit
    print(f"http://localhost:{args.port}")
    ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=args.out)).serve_forever()
