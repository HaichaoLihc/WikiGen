"""Step 2: the planner agent designs the table of contents. Step 3: checks send problems back to it."""
import json
import re

from .agent import ask_checked

MAX_SECTION_PAGES = 15  # one writer agent writes a whole first-level section, so a section cannot be huge
TOP_FILE_SHARE = 0.1   # the most important 10% of code files should each belong to some page

SYSTEM = """You plan the table of contents for a wiki that documents a codebase.

Explore the repository until you understand what it does and how it is built: README and docs, entry points, \
top-level folders, and the graph files below.

Organize the wiki around the system's conceptual architecture, not its
directory structure.

The top-level sections should represent the major areas a developer needs
to understand the system:
- Overview: the system's purpose, high-level architecture, and core concepts.
- Major subsystems: the primary components, layers, or capabilities that
  have distinct responsibilities within the architecture.
- Cross-cutting concerns: important mechanisms spanning multiple subsystems,
  such as security, configuration, persistence, or communication.
- Development: setup, building, testing, deployment, and contribution workflows.

Within each section, create sub-pages for its important components, mechanisms,
and workflows. Add another level when a subtopic is still broad.

Order sections to build understanding: orientation first, then core
architecture and subsystems, followed by supporting concerns and development.

Answer as JSON. For every page: a kebab-case id, a title, a one-sentence scope, its parent id ("" for a section), \
and the files a writer should start from. Do not add an Overview or a Glossary; they are added automatically."""

TOC_SCHEMA = {"type": "object", "required": ["pages"], "additionalProperties": False, "properties": {
    "pages": {"type": "array", "items": {
        "type": "object", "required": ["id", "title", "scope", "parent", "files"], "additionalProperties": False,
        "properties": {"id": {"type": "string"}, "title": {"type": "string"}, "scope": {"type": "string"},
                       "parent": {"type": "string"}, "files": {"type": "array", "items": {"type": "string"}}}}}}}

OVERVIEW = {"id": "overview", "title": "Overview", "parent": "", "files": [],
            "scope": "What the project is, its main parts and how they fit, and where to read next."}
GLOSSARY = {"id": "glossary", "title": "Glossary", "parent": "", "files": [],
            "scope": "Project-specific terms, each with a one-line meaning and the page that explains it."}


def subtree(toc, page_id):
    """The page with this id followed by all its descendants, in reading order."""
    pages = [p for p in toc if p["id"] == page_id]
    for child in [p for p in toc if p["parent"] == page_id]:
        pages += subtree(toc, child["id"])
    return pages


def depth(toc, page):
    parent_of = {p["id"]: p["parent"] for p in toc}
    level, current = 1, page["parent"]
    while current and level <= len(toc):  # the bound stops a parent cycle from looping forever
        level, current = level + 1, parent_of[current]
    return level


def outline(toc, page_id=""):
    """Indented text view of the tree: id, title and scope per page."""
    lines = []
    for page in [p for p in toc if p["parent"] == page_id]:
        lines.append(f"- {page['id']}: {page['title']} -- {page['scope']}")
        lines += ["  " + line for line in outline(toc, page["id"])]
    return lines


def tree_problems(pages, index):
    """Problems with the shape of a list of pages: ids, parents, depth and starting files."""
    ids = [p["id"] for p in pages]
    found = []
    for page in pages:
        if not re.fullmatch(r"[a-z0-9-]+", page["id"]) or page["id"] in ("overview", "glossary"):
            found.append(f"{page['id']}: id must be kebab-case and not 'overview' or 'glossary'")
        if page["parent"] and page["parent"] not in ids:
            found.append(f"{page['id']}: parent {page['parent']} does not exist")
        if not page["files"]:
            found.append(f"{page['id']}: needs at least one starting file")
        found += [f"{page['id']}: {f} is not a file in the repo" for f in page["files"] if f not in index.files]
    if len(set(ids)) < len(ids):
        found.append("page ids must be unique")
    return found or [f"{p['id']}: deeper than 3 levels" for p in pages if depth(pages, p) > 3]


def problems(toc, index, target_pages):
    """Problems with the planner's whole table of contents."""
    found = tree_problems(toc, index)
    if found:  # the checks below assume a well-formed tree
        return found
    for section in [p for p in toc if not p["parent"]]:
        size = len(subtree(toc, section["id"]))
        if size > MAX_SECTION_PAGES:
            found.append(f"section {section['id']} has {size} pages; split it (max {MAX_SECTION_PAGES})")
    if len(toc) > 1.5 * target_pages:
        found.append(f"{len(toc)} pages is too many; aim for about {target_pages}")

    important = index.top_files(index.score, max(20, int(len(index.score) * TOP_FILE_SHARE)))
    uncovered = set(important) - {f for p in toc for f in p["files"]}
    if len(uncovered) > 0.2 * len(important):
        found.append("these important files belong to no page; add them where they fit: " + ", ".join(sorted(uncovered)))
    return found


def plan(agent, index, target_pages):
    """Ask the planner for the table of contents until it passes the checks. Returns the list of pages."""
    def check(answer):
        try:
            return problems(json.loads(answer)["pages"], index, target_pages)
        except (ValueError, KeyError, TypeError):
            return ['answer with JSON only, shaped like {"pages": [...]}']

    prompt = (f"The repository has {len(index.score)} code files. Aim for about {target_pages} pages. "
              "Explore the graph files and the repository, then answer with the table of contents as JSON.")
    answer = ask_checked(agent, prompt, check, schema=TOC_SCHEMA, retries=3)
    if check(answer):
        raise RuntimeError("the planner's table of contents still has problems:\n" + "\n".join(check(answer)))
    return [OVERVIEW, *json.loads(answer)["pages"], GLOSSARY]
