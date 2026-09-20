import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_today import post_facebook, post_instagram, RAW_BASE, ROOT  # noqa: E402


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    start_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    with open(os.path.join(ROOT, "queue.json"), encoding="utf-8") as f:
        queue = json.load(f)

    for i in range(count):
        idx = (start_index + i) % len(queue)
        item = queue[idx]
        url = f"{RAW_BASE}/{item['path']}"
        print(f"\n=== burst {i+1}/{count} — item #{idx}: {item['path']} ===")
        fb_ok = post_facebook(item, url)
        ig_ok = post_instagram(item, url)
        print(f"Result — FB: {'OK' if fb_ok else 'FAILED'}, IG: {'OK' if ig_ok else 'FAILED'}")
        if i < count - 1:
            time.sleep(300)  # 5 minutes


if __name__ == "__main__":
    main()
