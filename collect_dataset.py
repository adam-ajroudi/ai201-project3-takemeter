#!/usr/bin/env python3
"""Collect and label r/nba comments for TakeMeter project."""

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

SUBREDDIT = "nba"
TARGET_PER_LABEL = 75
MIN_LEN = 40
MAX_LEN = 600
CACHE_PATH = Path("raw_posts.json")

STAT_PATTERNS = re.compile(
    r"\b(\d+\.?\d*\s*%|\d+\s*(ppg|rpg|apg|pts|reb|ast|per game|games|season|year|"
    r"three.?point|fg%|ts%|efg%|usage|minutes|win.?rate|record))\b",
    re.I,
)
COMPARISON_WORDS = re.compile(
    r"\b(compared to|versus|vs\.?|because|however|therefore|statistically|"
    r"efficiency|breakdown|analysis|numbers show|data|historically|"
    r"on average|per 100|per possession)\b",
    re.I,
)
HOT_TAKE_PATTERNS = re.compile(
    r"\b(overrated|underrated|trash|goat|best ever|worst|fire|trade him|"
    r"unpopular opinion|hot take|no way|absolutely|clearly the|easily|"
    r"never|always|disgrace|embarrassing|robbed|should be|needs to)\b",
    re.I,
)
REACTION_PATTERNS = re.compile(
    r"^(wow|lol|lmao|omg|yes!|no!|lets go|let's go|what a|insane|crazy|"
    r"bruh|damn|sheesh|yikes|pain|heartbreaking|beautiful|goat\b)",
    re.I,
)
EMOTIONAL = re.compile(
    r"(!{2,}|😭|🔥|💀|🐐|🤣|😂|!!!|\b(so happy|so mad|i'm done|i cant|i can't)\b)",
    re.I,
)


def fetch_api(endpoint, before=None, size=25):
    params = {"subreddit": SUBREDDIT, "size": size, "sort": "desc", "sort_type": "created_utc"}
    if before:
        params["before"] = before
    url = f"https://api.pullpush.io/reddit/search/{endpoint}/?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "TakeMeter/1.0 (AI201 project)"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp).get("data", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = min(60, 3 * (2 ** attempt))
                print(f"    rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
    return []


def clean_text(text):
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"http\S+", "", text)
    return text.strip()


def label_post(text):
    words = text.split()
    n = len(words)
    stat_hits = len(STAT_PATTERNS.findall(text))
    comp_hits = len(COMPARISON_WORDS.findall(text))
    hot_hits = len(HOT_TAKE_PATTERNS.findall(text))

    if (stat_hits >= 2 or (stat_hits >= 1 and comp_hits >= 1)) and n >= 25:
        return "analysis"
    if comp_hits >= 2 and n >= 35 and hot_hits == 0:
        return "analysis"
    if stat_hits >= 1 and n >= 50 and comp_hits >= 1:
        return "analysis"
    if n <= 18 and (REACTION_PATTERNS.search(text) or EMOTIONAL.search(text) or text.endswith("!")):
        return "reaction"
    if n <= 12:
        return "reaction"
    if EMOTIONAL.search(text) and n <= 30 and stat_hits == 0 and comp_hits == 0:
        return "reaction"
    if hot_hits >= 1 and stat_hits == 0 and n <= 80:
        return "hot_take"
    if hot_hits >= 2:
        return "hot_take"
    if stat_hits == 1 and hot_hits >= 1 and comp_hits == 0:
        return "hot_take"
    if n <= 25 and stat_hits == 0 and comp_hits == 0:
        return "reaction" if EMOTIONAL.search(text) else "hot_take"
    if stat_hits >= 1 or comp_hits >= 1:
        return "analysis"
    if hot_hits >= 1:
        return "hot_take"
    return "reaction" if n <= 22 else "hot_take"


def load_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return []


def save_cache(rows):
    CACHE_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_raw():
    rows = load_cache()
    seen = {r["text"] for r in rows}
    before_map = {"comment": None, "submission": None}
    endpoints = ["comment", "submission"]

    print(f"Starting collection ({len(rows)} cached)...")
    for round_num in range(80):
        counts = Counter(r["label"] for r in rows)
        if len(rows) >= 260 and all(counts.get(l, 0) >= TARGET_PER_LABEL + 25 for l in counts):
            break

        endpoint = endpoints[round_num % 2]
        batch = fetch_api(endpoint, before=before_map[endpoint], size=25)
        if not batch:
            time.sleep(5)
            continue
        before_map[endpoint] = batch[-1].get("created_utc")

        added = 0
        for item in batch:
            text = clean_text(item.get("body") or item.get("title") or item.get("selftext") or "")
            if len(text) < MIN_LEN or len(text) > MAX_LEN:
                continue
            if text in seen or text.lower() in ("[removed]", "[deleted]"):
                continue
            seen.add(text)
            rows.append({"text": text, "label": label_post(text), "notes": ""})
            added += 1

        save_cache(rows)
        counts = Counter(r["label"] for r in rows)
        print(f"  round {round_num + 1} ({endpoint}): +{added}, total={len(rows)} | {dict(counts)}")
        time.sleep(4)

    return rows


def balance_and_save(rows):
    by_label = {"analysis": [], "hot_take": [], "reaction": []}
    for row in rows:
        by_label[row["label"]].append(row)

    final = []
    for label in by_label:
        final.extend(by_label[label][:TARGET_PER_LABEL])

    counts = Counter(r["label"] for r in final)
    for label in ("analysis", "hot_take", "reaction"):
        need = TARGET_PER_LABEL - counts[label]
        if need > 0:
            final.extend(by_label[label][TARGET_PER_LABEL : TARGET_PER_LABEL + need])

    import random
    random.seed(42)
    random.shuffle(final)

    with open("dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
        writer.writeheader()
        writer.writerows(final)

    dist = Counter(r["label"] for r in final)
    print(f"\nSaved {len(final)} examples to dataset.csv")
    print("Label distribution:", dict(dist))


if __name__ == "__main__":
    rows = collect_raw()
    balance_and_save(rows)
