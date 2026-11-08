"""Fetch governor-elect platform pages into data/interim/ingest/platforms/ and platforms.csv.

Each candidate has seed URLs; same-site links under an issues path are followed once.
An existing platforms/<candidate_id>.txt (fetched or saved by hand) is never refetched;
delete it to fetch again.
"""

import argparse
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "interim" / "ingest"
CANDIDATES = json.loads(Path(__file__).with_name("candidates.json").read_text())
SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form"}
BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "div", "br", "section"}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip, self.parts, self.links = 0, [], []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "a":
            self.links += [v for k, v in attrs if k == "href" and v]

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(re.sub(r"\s+", " ", data))  # source newlines are spaces


def to_text(html):
    p = Text()
    p.feed(html)
    lines = (re.sub(r"\s+", " ", line).strip() for line in "".join(p.parts).split("\n"))
    return [line for line in lines if line], p.links


def get(url):
    r = requests.get(url, timeout=30, headers={"User-Agent": "poliscope-ingest"})
    r.raise_for_status()
    return r.text


def crawl(seeds, follow):
    queue, seen, pages = list(seeds), set(), []
    host = urlparse(seeds[0]).netloc
    while queue:
        url = queue.pop(0).split("#")[0].rstrip("/")
        if url in seen:
            continue
        seen.add(url)
        lines, links = to_text(get(url))
        pages.append(lines)
        for link in links:
            u = urljoin(url + "/", link)
            if urlparse(u).netloc == host and re.search(follow, urlparse(u).path):
                queue.append(u)
    # Drop boilerplate lines (menus, buttons) that repeat on several pages.
    counts = pd.Series([line for page in pages for line in set(page)]).value_counts()
    repeated = set(counts[counts > 1].index) if len(pages) > 2 else set()
    kept, out = set(), []
    for page in pages:
        for line in page:
            if line not in repeated and line not in kept:
                kept.add(line)
                out.append(line)
    return "\n".join(out) + "\n", sorted(seen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice30", action="store_true")  # accepted; always all 5
    ap.parse_args()
    (OUT / "platforms").mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    old = (
        pd.read_csv(OUT / "platforms.csv") if (OUT / "platforms.csv").exists() else None
    )
    rows = []
    for c in CANDIDATES:
        path = OUT / "platforms" / f"{c['candidate_id']}.txt"
        retrieved = today
        # Saved texts are kept: campaign sites change or vanish after the election.
        if path.exists():
            if old is not None and c["candidate_id"] in set(old.candidate_id):
                retrieved = old.set_index("candidate_id").retrieved_at[
                    c["candidate_id"]
                ]
        else:
            text, pages = crawl(c["seeds"], c.get("follow", r"^/issues?/."))
            path.write_text(text, encoding="utf-8")
            print(c["candidate_id"], len(pages), "pages")
        text = path.read_text(encoding="utf-8")
        rows.append(
            {
                "candidate_id": c["candidate_id"],
                "name": c["name"],
                "state": c["state"],
                "party": c["party"],
                "url": c["seeds"][0],
                "retrieved_at": retrieved,
                "text_path": str(path.relative_to(ROOT)),
                "n_chars": len(text),
            }
        )
        print(c["candidate_id"], len(text.split()), "words")
    df = pd.DataFrame(rows)
    assert len(df) == 5 and df.candidate_id.is_unique
    assert (df.party.value_counts().reindex(["D", "R"]) >= 2).all()
    df.to_csv(OUT / "platforms.csv", index=False)


if __name__ == "__main__":
    main()
