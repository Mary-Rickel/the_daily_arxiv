#!/usr/bin/env python3
"""
the_daily_arxiv.py
------------------
Fetches recent arXiv papers, ranks them by keyword relevance,
sends macOS notifications for the top N, and opens each paper
in Google Chrome. Tracks seen papers to avoid duplicates across runs.
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import sys
import subprocess
import time
from datetime import datetime, timezone, timedelta

#  paths 
DIR         = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(DIR, "config.json")
SEEN_FILE   = os.path.join(DIR, "seen_papers.json")
LOG_FILE    = os.path.join(DIR, "daily_arxiv.log")

# default configuration
DEFAULT_CONFIG = {
    "category":          "astro-ph.GA",
    "keywords":          ["star formation", "dark matter", "JWST", "galactic"],
    "max_papers":        80,
    "max_notifications": 10,
    "delay_between":     6,
    "only_matched":      True,
    "seen_expiry_days":  7    # forget seen papers after this many days
}

# keeping log
def log(msg):
    ts   = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

# Open config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    return DEFAULT_CONFIG.copy()

# "Seen" paper tracking 
def load_seen():
    """Load the set of already-notified paper IDs with timestamps."""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return json.load(f)
    return {}

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=2)

def purge_old_seen(seen, expiry_days):
    """Remove entries older than expiry_days to keep the file lean."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=expiry_days)).isoformat()
    return {k: v for k, v in seen.items() if v >= cutoff}

def mark_seen(seen, paper_ids):
    now = datetime.now(timezone.utc).isoformat()
    for pid in paper_ids:
        seen[pid] = now
    return seen

# Fetch papers from Arxiv API
def fetch_papers(category, max_results=80):
    url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query=cat:{category}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={max_results}&start=0"
    )
    log(f"Fetching {category} (max {max_results})…")
    headers = {'User-Agent': 'the_daily_arxiv/1.0 (daily paper notifier; https://github.com/Mary-Rickel/the_daily_arxiv)'}
    time.sleep(3) ## MER added for now to deal with 429 error
    req = urllib.request.Request(url, headers=headers) ## MER added user agent bc 429 error
    with urllib.request.urlopen(req, timeout=30) as r:
        xml_data = r.read()

    ns    = {"atom": "http://www.w3.org/2005/Atom"}
    root  = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", ns):
        raw_id    = entry.find("atom:id", ns).text.strip()
        arxiv_id  = raw_id.split("/abs/")[-1]
        title     = (entry.find("atom:title",   ns).text or "").strip().replace("\n", " ")
        abstract  = (entry.find("atom:summary", ns).text or "").strip().replace("\n", " ")
        authors   = [a.find("atom:name", ns).text.strip()
                     for a in entry.findall("atom:author", ns)]
        published = entry.find("atom:published", ns).text.strip()  # full ISO string
        updated   = entry.find("atom:updated",   ns).text.strip()
        papers.append({
            "id":        arxiv_id,
            "url":       f"https://arxiv.org/abs/{arxiv_id}",
            "title":     title,
            "abstract":  abstract,
            "authors":   authors,
            "published": published,   # full ISO for date filtering
            "published_date": published[:10],
        })
    log(f"Got {len(papers)} papers")
    return papers

# Date filtering
def last_business_day(d):
    """Step back from date d to the most recent weekday."""
    d -= timedelta(days=1)
    while d.weekday() >= 5:  # 5=Saturday, 6=Sunday
        d -= timedelta(days=1)
    return d

def filter_by_date(papers, run_type):
    """
    AM run → today (if weekday) or last business day, plus the one before
    PM run → same but goes one day further back
    Skips weekends entirely in the lookback window.
    """
    now   = datetime.now(timezone.utc)
    today = now.date()

    # If today is a weekend, treat it as the last business day
    ref = today
    while ref.weekday() >= 5:
        ref -= timedelta(days=1)

    # Cutoff = 1 business day back for AM, 2 for PM
    steps = 1 if run_type == "am" else 2
    cutoff = ref
    for _ in range(steps):
        cutoff = last_business_day(cutoff)

    filtered = [p for p in papers if p["published_date"] >= str(cutoff)]
    log(f"Date filter ({run_type.upper()}, cutoff {cutoff}): {len(filtered)} / {len(papers)} papers")
    return filtered

# Duplicate filter 
def filter_seen(papers, seen):
    fresh = [p for p in papers if p["id"] not in seen]
    dupes = len(papers) - len(fresh)
    if dupes:
        log(f"Skipping {dupes} already-seen paper(s)")
    return fresh

# Ranking system
def rank_papers(papers, keywords):
    """
    Rank 1 — 5+ keyword hits  (high interest)
    Rank 2 — 2–4 keyword hits (moderate interest)
    Rank 3 — 1 keyword hit    (some interest)
    Unranked — 0 hits         (excluded if only_matched=True)

    Within each rank, papers are sorted by hit count descending.
    """
    kws = [k.lower() for k in keywords]
    ranked = []
    for p in papers:
        hay  = (p["title"] + " " + p["abstract"]).lower()
        hits = [k for k in kws if k in hay]
        n    = len(hits)
        if n >= 5:
            rank = 1
        elif n >= 2:
            rank = 2
        elif n == 1:
            rank = 3
        else:
            rank = 99   # no match

        p["_hits"]      = hits
        p["_hit_count"] = n
        p["_rank"]      = rank
        ranked.append(p)

    # Sort: rank ascending (1 best), then hit count descending within rank
    ranked.sort(key=lambda p: (p["_rank"], -p["_hit_count"]))
    return ranked

def select_papers(ranked, max_notify, only_matched):
    """Pick up to max_notify papers, prioritising rank 1 > 2 > 3."""
    pool = [p for p in ranked if p["_rank"] <= 3] if only_matched \
           else ranked
    return pool[:max_notify]

# Notifications 
def has_terminal_notifier():
    try:
        subprocess.run(["terminal-notifier", "-help"], capture_output=True, timeout=3)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

RANK_PREFIX = {1: "Rank 1", 2: "Rank 2", 3: "Rank 3"}

def notify_terminal_notifier(title, subtitle, body, url):
    subprocess.run([
        "terminal-notifier",
        "-title",    "The Daily arXiv",
        "-subtitle", subtitle,
        "-message",  body,
        "-open",     url,
        "-sound",    "default",
        "-group",    "daily-arxiv",
    ], capture_output=True)
    subprocess.run(["open", "-a", "Google Chrome", url])

def notify_osascript(title, subtitle, body, url):
    t = title.replace('"', '\\"')
    s = subtitle.replace('"', '\\"')
    b = body.replace('"', '\\"')
    script = f'display notification "{b}" with title "The Daily arXiv" subtitle "{s}"'
    subprocess.run(["osascript", "-e", script], capture_output=True)
    subprocess.run(["open", "-a", "Google Chrome", url])

def send_notification(paper, use_tn):
    rank       = paper.get("_rank", 3)
    prefix     = RANK_PREFIX.get(rank, "★")
    title      = paper["title"]
    if len(title) > 75:
        title  = title[:72] + "…"

    authors    = paper["authors"]
    author_str = authors[0] if authors else "Unknown"
    if len(authors) > 1:
        author_str += f" +{len(authors)-1}"

    hits        = paper.get("_hits", [])
    keyword_str = f"{', '.join(hits[:3])}" if hits else paper["id"]
    subtitle    = f"{prefix}  {keyword_str}  ·  {author_str}"
    abstract    = paper["abstract"]
    snippet     = abstract[:140] + "…" if len(abstract) > 140 else abstract

    if use_tn:
        notify_terminal_notifier(title, subtitle, snippet, paper["url"])
    else:
        notify_osascript(title, subtitle, snippet, paper["url"])

def send_summary(total_fetched, selected, run_type, use_tn):
    counts  = {1: sum(1 for p in selected if p["_rank"]==1),
               2: sum(1 for p in selected if p["_rank"]==2),
               3: sum(1 for p in selected if p["_rank"]==3)}
    body = (f"Rank1:{counts[1]}  Rank2:{counts[2]}  Rank3:{counts[3]}"
        f"  ·  {total_fetched} fetched  ·  {run_type.upper()} run")
    if use_tn:
        subprocess.run([
            "terminal-notifier",
            "-title",   "The Daily arXiv",
            "-message", body,
            "-sound",   "Submarine",
            "-group",   "daily-arxiv-summary",
        ], capture_output=True)
    else:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{body}" with title "☀ The Daily arXiv"'
        ], capture_output=True)

# Settings 
def edit_settings():
    print(f"\nConfig: {CONFIG_FILE}\n")
    cfg = load_config()
    print(json.dumps(cfg, indent=2))
    subprocess.run(["open", "-e", CONFIG_FILE])

# Main
def main():
    if "--settings" in sys.argv or "--config" in sys.argv:
        edit_settings()
        return

    if "--check" in sys.argv:
        use_tn = has_terminal_notifier()
        print(f"terminal-notifier: {'✓ found' if use_tn else '✗ not found'}")
        print(f"Config:     {CONFIG_FILE}")
        print(f"Seen log:   {SEEN_FILE}")
        print(json.dumps(load_config(), indent=2))
        return

    if "--clear-seen" in sys.argv:
        if os.path.exists(SEEN_FILE):
            os.remove(SEEN_FILE)
            print("Cleared seen-papers log.")
        else:
            print("No seen-papers log found.")
        return

    # Determine run type
    run_type = "pm" if "--pm" in sys.argv else "am"
    # Auto-detect if not specified: PM if hour >= 11
    if "--am" not in sys.argv and "--pm" not in sys.argv:
        run_type = "pm" if datetime.now().hour >= 11 else "am"
    log(f"=== The Daily arXiv — {run_type.upper()} run ===")

    cfg    = load_config()
    use_tn = has_terminal_notifier()

    try:
        # Load seen papers and purge old ones
        seen = load_seen()
        seen = purge_old_seen(seen, cfg.get("seen_expiry_days", 7))

        # Fetch, date-filter, deduplicate, rank, select
        papers   = fetch_papers(cfg["category"], cfg["max_papers"])
        papers   = filter_by_date(papers, run_type)
        papers   = filter_seen(papers, seen)
        ranked   = rank_papers(papers, cfg["keywords"])
        selected = select_papers(ranked, cfg["max_notifications"], cfg["only_matched"])

        log(f"Selected {len(selected)} papers to notify")


        # Mark selected papers as seen
        seen = mark_seen(seen, [p["id"] for p in selected])
        save_seen(seen)

        # Send summary banner
        send_summary(len(papers), selected, run_type, use_tn)
        time.sleep(2)

        # Send one notification per paper
        for paper in selected:
            send_notification(paper, use_tn)
            time.sleep(cfg["delay_between"])

    except Exception as e:
        log(f"ERROR: {e}")
        if use_tn:
            subprocess.run([
                "terminal-notifier",
                "-title",   "The Daily arXiv — Error",
                "-message", str(e)[:200],
                "-group",   "daily-arxiv-error"
            ], capture_output=True)
        else:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{str(e)[:100]}" with title "Daily arXiv Error"'
            ], capture_output=True)

if __name__ == "__main__":
    main()
