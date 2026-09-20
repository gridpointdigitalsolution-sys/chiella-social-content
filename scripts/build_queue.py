import csv
import itertools
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
SHEET = os.path.join(ROOT, "..", "CONTENT_ENGINE", "2_FINISHED", "FINISHED_POSTING_SHEET.csv")

random.seed(20260920)

REAL_CAPTIONS = {
    "cakes": [
        "Every cake is baked and decorated to order.",
        "One of our cake builds, ready for its big moment.",
        "Cakes finished the way the client pictured them.",
    ],
    "cooking_stills": [
        "From our kitchen, prepped for the day's event.",
        "A look at the food side of what we do.",
        "Plated and ready to serve.",
    ],
    "cooking_video": [
        "A little behind-the-scenes from the kitchen.",
        "How the food comes together on event day.",
    ],
    "event": [
        "A look at one of our recent setups.",
        "Décor and set-up from a past event.",
        "One of the halls we transformed.",
    ],
    "rentals_stills": [
        "Chairs, tables, and more — sourced and set up by our team.",
        "Rental pieces ready for the next event.",
    ],
    "rentals_video": [
        "A look at our rental setup in motion.",
    ],
    "go": [
        "Nigerian events, done right.",
        "Chi'Ella Events & Hospitality.",
        "One-stop for catering, décor, rentals, and more.",
    ],
    "dp": [
        "Chi'Ella Events & Hospitality.",
        "Cook · serve · seat · clothe — the full owambe experience.",
    ],
}

HANDLES = "@chiellaevent (IG/TikTok) · ChiellaEvents (FB) · @ChiellaEvents (X)"


def load_sheet():
    rows = {}
    with open(SHEET, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows[row["output_file"]] = row
    return rows


def real_items(folder, kind):
    d = os.path.join(ASSETS, folder)
    out = []
    if not os.path.isdir(d):
        return out
    for fname in sorted(os.listdir(d)):
        cap = random.choice(REAL_CAPTIONS[folder])
        out.append(dict(
            type=kind,
            path=f"assets/{folder}/{fname}",
            caption_fb=f"{cap}\n\n{HANDLES}",
            caption_ig=f"{cap}\n\n{HANDLES}",
            source=folder,
        ))
    return out


def banner_items(folder, sheet):
    d = os.path.join(ASSETS, folder)
    out = []
    if not os.path.isdir(d):
        return out
    for fname in sorted(os.listdir(d)):
        key_edu = f"educational/{fname}"
        key_inf = f"informational/{fname}"
        row = sheet.get(key_edu) or sheet.get(key_inf)
        if row:
            fb, ig = row["caption_facebook"], row["caption_instagram"]
        else:
            cap = random.choice(REAL_CAPTIONS.get(folder, ["Chi'Ella Events & Hospitality."]))
            fb = ig = f"{cap}\n\n{HANDLES}"
        out.append(dict(type="image", path=f"assets/{folder}/{fname}", caption_fb=fb, caption_ig=ig, source=folder))
    return out


def main():
    sheet = load_sheet()
    groups = [
        banner_items("edu", sheet),
        banner_items("inf", sheet),
        real_items("cakes", "image"),
        real_items("cooking_stills", "image"),
        real_items("cooking_video", "video"),
        real_items("event", "image"),
        real_items("rentals_stills", "image"),
        real_items("rentals_video", "video"),
        banner_items("go", sheet),
        banner_items("dp", sheet),
    ]
    for g in groups:
        random.shuffle(g)

    # round-robin interleave so nothing sits stacked by type
    queue = [item for item in itertools.chain.from_iterable(itertools.zip_longest(*groups)) if item]

    out_path = os.path.join(ROOT, "queue.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=1)
    print(f"queue built: {len(queue)} items -> {out_path}")
    print(f"at 3/day that's {len(queue)/3:.0f} days of content")


if __name__ == "__main__":
    main()
