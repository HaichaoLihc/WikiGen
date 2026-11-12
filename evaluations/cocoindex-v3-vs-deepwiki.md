# cocoindex: our wiki (v3) against DeepWiki

Both wikis describe `cocoindex-io/cocoindex` at commit `f7078f01`. Ours is `out/cocoindex-v3`; DeepWiki's pages are saved in `out/deepwiki/cocoindex.json`.

## Whole-wiki numbers

| | Ours (v3) | DeepWiki |
|---|---|---|
| Pages | 58 | 55, plus a glossary |
| Words (median per page) | 34,014 (545) | 41,985 (754) |
| Citations per page | 30.7 | 30.3 |
| Citations that point to real files and lines | 100% | 98.3% |
| Citations into source code | 79% | 58% |
| Citations into docs, examples and tests | 13% | 32% |
| Files cited | 302 | 260 |
| Most important files cited (top 57 by graph score) | 47 | 45 |
| Diagrams | 57 | 124 |
| Tables | 46 | 54 |
| Code excerpts | 4 | 41 |

DeepWiki has 28 invalid citations, including 8 files that do not exist at that commit (for example `rust/state_store/storage.rs`).

## Blind review of four matched pages

Each reviewer saw two pages labelled A and B with the origin hidden, fact-checked six claims per page against the repo, opened five citations per page, and rated both from 1 to 5.

| Topic | Claims correct (ours / DeepWiki) | Citations supporting their sentence (ours / DeepWiki) | Verdict |
|---|---|---|---|
| Overview | 6 of 6 / 3 of 6 | 5 of 5 / 2 of 5 | Ours better |
| Functions and change detection | 6 of 6 / 4 of 6 | 5 of 5 / 3 of 5 | Ours better |
| Targets | 6 of 6 / 3 of 6 | 5 of 5 / 3 of 5 | Ours better, narrowly |
| Engine internals | 6 of 6 / 3 of 6 | 5 of 5 / 3 of 5 | Ours better |
| Total | 24 of 24 / 13 of 24 | 20 of 20 / 11 of 20 | |

| Average rating | Ours | DeepWiki |
|---|---|---|
| Accuracy | 5.0 | 2.5 |
| Depth | 3.3 | 2.3 |
| Clarity | 4.0 | 3.0 |
| Useful to a newcomer | 3.8 | 3.0 |
| Useful to a coding agent | 3.8 | 2.3 |

## Where ours was better

- No sampled claim was wrong; DeepWiki had 10 wrong, such as an `app.setup()` method that does not exist.
- Citations sit next to the claim they prove. DeepWiki often cites import blocks, a README line or a blog post.
- File and line pointers are right. DeepWiki's diagrams label the LMDB store with the wrong directory.

## Where DeepWiki was better

- More breadth per page: connector lists, a crate table, an LMDB key table.
- About twice the diagrams per page and ten times the code excerpts.
- Section pages that stand alone. Our targets section page scored 2 for depth because it never named `TargetHandler` or `reconcile`.

## Limits

- Four pairs only, with six claims and five citations sampled per page.
- Three of our four pages were section introductions matched against DeepWiki topic pages.
- Blinding was imperfect: stray characters were left at the end of DeepWiki's pages and links were stripped from ours.
- The reviewers were AI models.

This review led to two changes in later versions: fuller section main pages, and more varied formats (diagram types and code excerpts).
