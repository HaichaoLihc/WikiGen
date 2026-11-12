"""Steps 4-7: writers reshape their sections and write the pages, the planner writes overview and
glossary, then assembly."""
import json
import re
from collections import defaultdict

from . import agent as agents
from .agent import ask_checked
from .plan import TOC_SCHEMA, outline, subtree, tree_problems

CITATION = re.compile(r"\[([^\[\]\s:]+):(\d+)(?:-(\d+))?\]")  # [path/to/file.py:10-42]
LINK = re.compile(r"\]\(([a-z0-9-]+)\.md\)")                   # [text](other-page.md)
MAX_SECTION_PAGES = 18  # a writer may grow its section up to this many pages

SYSTEM = """You write pages of a wiki that documents a codebase, reading the repository as you go. Readers are \
engineers new to the project and coding agents. Write so a busy reader gets the point fast.

Content:
- Explain how the thing works and why it is built that way: the mechanism, the decisions behind it, and the \
edge cases that would surprise a newcomer.
- Read the code before writing about it. If you cannot verify something, leave it out.
- Use the identifiers and wording of the code and docs. Do not coin new names.
- Stay inside the page's scope; link to other pages as [Title](page-id.md) instead of repeating them.

Form: pick the format that carries each idea best, and vary it. Prose plus one flowchart is rarely the best page.
- A mermaid diagram on most pages, of the type that fits the idea: sequenceDiagram for calls between components \
over time, classDiagram for types and how they relate, stateDiagram-v2 for a lifecycle or state machine, flowchart \
for data or control flow. Label nodes with real names from the code and keep labels short. A flowchart \
node whose label has spaces or punctuation needs an id and a quoted label, like engine["target-state engine"].
- A table for parallel items: options, parameters, variants, components and their roles, comparisons.
- A numbered list for steps that happen in order.
- A code excerpt of 5-15 lines, copied from the repo and cited, wherever the page covers an API, a usage pattern \
or a key data structure: show the real signature or the real call.
- Prose, in short paragraphs, for reasoning.

Style:
- Concise: 400-900 words. No filler, no restating the heading, no "this page describes", no closing recap.
- Lead each section with its main point.

Citations:
- Back each paragraph, table and diagram with the lines that prove it, written as [path/to/file.py:10-42]: path \
relative to the repo root, real line numbers. One or two precise citations beat a string of them. Never cite \
from memory.

Skeleton: "# <title>", then "## Summary" (2-4 sentences a reader can stop after), then the body, then "## Terms" \
listing the project-specific terms this page explains as "- **Term**: one-line meaning".

When asked for a page, answer with the page's markdown only."""


SECTION_PAGE = """This is the section's main page, and a reader may read only this one. Explain the section's \
core mechanism from end to end: what happens, in what order, and why. Include a table of the key types or functions \
and the files that define them. Then point to each sub-page for the detail it adds. Aim for 700-1200 words."""


class Wiki:
    def __init__(self, index, toc, out):
        self.index, self.toc, self.out = index, toc, out
        self.ids = {p["id"] for p in toc}

    def text(self, page_id):
        path = self.out / f"{page_id}.md"
        return path.read_text() if path.exists() else ""

    def bad_citations(self, markdown):
        """Citations that point at a missing file or outside its line range, as {citation: reason}."""
        bad = {}
        for match in CITATION.finditer(markdown):
            path, start, end = match[1], int(match[2]), int(match[3] or match[2])
            if path not in self.index.files:
                bad[match[0]] = "no such file"
            elif not 1 <= start <= end <= len((self.index.repo / path).read_text(errors="replace").splitlines()):
                bad[match[0]] = "line range is outside the file"
        return bad

    def problems(self, page_id, markdown):
        plain = page_id not in ("overview", "glossary")
        found = [f"{citation}: {reason}" for citation, reason in self.bad_citations(markdown).items()]
        found += [f"link to unknown page {target}.md" for target in LINK.findall(markdown) if target not in self.ids]
        if not markdown.startswith("# "):
            found.append('the answer must be only the page, starting with "# <title>"')
        if plain and not ("## Summary" in markdown and "## Terms" in markdown):
            found.append('the page needs "## Summary" and "## Terms" sections')
        if page_id != "glossary" and len(CITATION.findall(markdown)) < 3:
            found.append("the page needs at least 3 code citations like [path/to/file.py:10-42]")
        return found

    def write(self, agent, page_id, prompt):
        """Ask for one page, let the agent fix what the checks find, and save it."""
        markdown = ask_checked(agent, prompt, lambda answer: self.problems(page_id, answer))
        for citation in self.bad_citations(markdown):  # still unverifiable after the retries: drop it
            markdown = markdown.replace(citation, "")
        (self.out / f"{page_id}.md").write_text(markdown)
        # Saved after every page, so an interrupted run still shows what it spent.
        (self.out / "usage.json").write_text(json.dumps(dict(agents.usage), indent=1))


def section_of(markdown, heading):
    """Text under one '## heading', up to the next '## '."""
    match = re.search(rf"^## {heading}\s*\n(.*?)(?=^## |\Z)", markdown, re.S | re.M)
    return match[1].strip() if match else ""


def shape_section(toc, index, agent, section):
    """The writer explores its section and decides the section's final pages. Returns that list.

    The planner's sub-pages are a proposal: the writer may keep, split, merge, rename or add sub-pages.
    Only the section page itself is fixed. No page is written yet, so other writers can still be told
    the final page list before they link to it.
    """
    planned = subtree(toc, section["id"])
    planned_ids = {p["id"] for p in planned}
    prefix = section["id"] + "-"

    def check(answer):
        try:
            pages = json.loads(answer)["pages"]
        except (ValueError, KeyError, TypeError):
            return ['answer with JSON only, shaped like {"pages": [...]}']
        found = tree_problems(pages, index)
        if not pages or pages[0]["id"] != section["id"] or pages[0]["parent"]:
            found.append(f"the first page must be the section page '{section['id']}' with parent \"\"")
        found += [f"{p['id']}: must be inside the section; set its parent to a page in your list"
                  for p in pages[1:] if not p["parent"]]
        # New ids carry the section's prefix, so two writers working in parallel cannot pick the same id.
        found += [f"{p['id']}: a new page's id must start with '{prefix}'"
                  for p in pages if p["id"] not in planned_ids and not p["id"].startswith(prefix)]
        if len(pages) > MAX_SECTION_PAGES:
            found.append(f"{len(pages)} pages is too many for one section (max {MAX_SECTION_PAGES})")
        return found

    proposal = "\n".join(f"- {p['id']} (parent: {p['parent'] or 'none'}): {p['title']} -- {p['scope']}\n"
                         f"  start from: {', '.join(p['files'])}" for p in planned)
    prompt = ("Table of contents planned for the whole wiki:\n" + "\n".join(outline(toc))
              + f"\n\nYou own the section '{section['id']}'. The planner proposed these pages for it:\n{proposal}\n\n"
              "Explore this section's code first. Then decide the section's final pages. The proposal is a starting "
              "point: keep what works, and split, merge, rename or add sub-pages where the code calls for it, "
              f"for example a mechanism that deserves its own page. Up to 3 levels deep and {MAX_SECTION_PAGES} pages. "
              f"Keep the section page '{section['id']}' first. Reuse the proposed id when you keep a page; a new "
              f"page's id must start with '{prefix}'. Answer with the section's full page list as JSON.")
    answer = ask_checked(agent, prompt, check, schema=TOC_SCHEMA, retries=3)
    if check(answer):
        return planned  # the writer's list never passed the checks: fall back to the planner's
    return subtree(json.loads(answer)["pages"], section["id"])  # in reading order: parents before children


def write_section(wiki, agent, section):
    """One writer agent writes every page of its section, in the conversation it used to shape the section."""
    pages = subtree(wiki.toc, section["id"])
    intro = ("Final table of contents (for links, and to respect other pages' scopes):\n"
             + "\n".join(outline(wiki.toc))
             + f"\n\nYou will write the {len(pages)} page(s) of section '{section['id']}', one at a time.\n\n")
    # Reading order lists a parent before its children; reversed, every page comes after its sub-pages.
    for page in reversed(pages):
        if wiki.text(page["id"]):
            continue  # already written by an earlier run
        main_page = page is pages[0] and len(pages) > 1
        wiki.write(agent, page["id"], intro + f"Write the page '{page['id']}': {page['title']}\n"
                   f"Scope: {page['scope']}\nStart from: {', '.join(page['files'])}"
                   + (f"\n\n{SECTION_PAGE}" if main_page else ""))
        intro = ""


def write_overview_and_glossary(wiki, agent):
    """The planner writes the two pages that depend on all the others, from their summaries and terms."""
    digest = "\n\n".join(f"### {p['id']}: {p['title']}\n{section_of(wiki.text(p['id']), 'Summary')}\n"
                         f"Terms:\n{section_of(wiki.text(p['id']), 'Terms')}"
                         for p in wiki.toc if p["id"] not in ("overview", "glossary"))
    intro = ("All other wiki pages are written. Table of contents:\n" + "\n".join(outline(wiki.toc))
             + f"\n\nSummary and terms of each page:\n\n{digest}\n\n"
             "Two pages remain; they need no Summary or Terms sections. Follow these rules:\n" + SYSTEM + "\n\n")
    wiki.write(agent, "overview", intro + "Write the page 'overview': what the project is, its main parts and how "
               "they fit together, and a guide to the sections with links. Cite code, not the other pages. "
               "Include a diagram of the main parts and a table of the sections.")
    wiki.write(agent, "glossary", "Write the page 'glossary': every project-specific term from the lists above, "
               "merged and alphabetical, as '**Term**: one-line meaning. See [Page](page-id.md).' "
               "Note aliases where two names mean the same thing.")


def assemble(wiki):
    """Write the index for humans and agents, the file-to-page map, and a health report."""
    depth = {}
    for page in wiki.toc:  # the toc is in reading order, so a parent is always seen before its children
        depth[page["id"]] = depth.get(page["parent"], -1) + 1
    lines = ["# Wiki", "", "> Generated documentation. Each page cites the source files it describes.", ""]
    lines += [f"{'  ' * depth[p['id']]}- [{p['title']}]({p['id']}.md): {p['scope']}" for p in wiki.toc]
    for name in ("README.md", "llms.txt"):
        (wiki.out / name).write_text("\n".join(lines) + "\n")

    pages_citing = defaultdict(set)
    for page in wiki.toc:
        for path, *_ in CITATION.findall(wiki.text(page["id"])):
            pages_citing[path].add(page["id"])
    (wiki.out / "file_map.json").write_text(json.dumps({f: sorted(ids) for f, ids in sorted(pages_citing.items())}, indent=1))

    important = wiki.index.top_files(wiki.index.score, max(20, len(wiki.index.score) // 10))
    citations = [len(CITATION.findall(wiki.text(p["id"]))) for p in wiki.toc]
    report = {"pages": len(wiki.toc), "pages_missing": [p["id"] for p in wiki.toc if not wiki.text(p["id"])],
              "words": sum(len(wiki.text(p["id"]).split()) for p in wiki.toc),
              "citations_per_page": round(sum(citations) / len(citations), 1),
              "diagrams": sum(wiki.text(p["id"]).count("```mermaid") for p in wiki.toc),
              "tables": sum(len(re.findall(r"^\|[-: |]+\|\s*$", wiki.text(p["id"]), re.M)) for p in wiki.toc),
              "files_cited": len(pages_citing),
              "important_files_cited": f"{sum(f in pages_citing for f in important)} of {len(important)}",
              "tokens": dict(agents.usage)}
    return report
