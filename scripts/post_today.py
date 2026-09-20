import datetime
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

GRAPH = "https://graph.facebook.com/v21.0"
START_DATE = datetime.date(2026, 9, 21)
SLOTS = ["morning", "afternoon", "evening"]

PAGE_TOKEN = os.environ["META_PAGE_TOKEN"]
PAGE_ID = os.environ["FB_PAGE_ID"]
IG_ID = os.environ["IG_USER_ID"]
RAW_BASE = os.environ["RAW_BASE"]  # e.g. https://raw.githubusercontent.com/owner/repo/main


def load_queue():
    with open(os.path.join(ROOT, "queue.json"), encoding="utf-8") as f:
        return json.load(f)


def post_facebook(item, url):
    caption = item["caption_fb"]
    if item["type"] == "video":
        r = requests.post(f"{GRAPH}/{PAGE_ID}/videos", data={
            "file_url": url, "description": caption, "access_token": PAGE_TOKEN,
        })
    else:
        r = requests.post(f"{GRAPH}/{PAGE_ID}/photos", data={
            "url": url, "caption": caption, "access_token": PAGE_TOKEN,
        })
    print("FB:", r.status_code, r.text[:300])
    return r.ok


def post_instagram(item, url):
    caption = item["caption_ig"]
    if item["type"] == "video":
        r = requests.post(f"{GRAPH}/{IG_ID}/media", data={
            "video_url": url, "caption": caption, "media_type": "REELS", "access_token": PAGE_TOKEN,
        })
    else:
        r = requests.post(f"{GRAPH}/{IG_ID}/media", data={
            "image_url": url, "caption": caption, "access_token": PAGE_TOKEN,
        })
    print("IG container:", r.status_code, r.text[:300])
    if not r.ok:
        return False
    creation_id = r.json().get("id")
    if not creation_id:
        return False

    # video containers need time to process before publish
    if item["type"] == "video":
        for _ in range(10):
            time.sleep(15)
            s = requests.get(f"{GRAPH}/{creation_id}", params={
                "fields": "status_code", "access_token": PAGE_TOKEN,
            })
            status = s.json().get("status_code")
            print("IG video status:", status)
            if status == "FINISHED":
                break
            if status == "ERROR":
                return False

    p = requests.post(f"{GRAPH}/{IG_ID}/media_publish", data={
        "creation_id": creation_id, "access_token": PAGE_TOKEN,
    })
    print("IG publish:", p.status_code, p.text[:300])
    return p.ok


def main():
    slot_name = sys.argv[1] if len(sys.argv) > 1 else "morning"
    slot_idx = SLOTS.index(slot_name)

    queue = load_queue()
    day_number = (datetime.date.today() - START_DATE).days
    if day_number < 0:
        print("before start date, nothing to post yet")
        return
    idx = day_number * 3 + slot_idx
    if idx >= len(queue):
        idx = idx % len(queue)  # loop back to start once exhausted
        print(f"queue exhausted once, looping (effective index {idx})")

    item = queue[idx]
    url = f"{RAW_BASE}/{item['path']}"
    print(f"Day {day_number} [{slot_name}] item #{idx}: {item['path']}")

    fb_ok = post_facebook(item, url)
    ig_ok = post_instagram(item, url)
    print(f"Result — FB: {'OK' if fb_ok else 'FAILED'}, IG: {'OK' if ig_ok else 'FAILED'}")


if __name__ == "__main__":
    main()
