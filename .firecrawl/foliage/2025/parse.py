import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
base = r".firecrawl/foliage/2025"

for name in ["haguro-ig-search", "fs-maple2", "wn-kami-forecast"]:
    path = os.path.join(base, f"{name}.json")
    print("====", name, "====")
    if not os.path.exists(path):
        print("MISSING")
        continue
    d = json.load(open(path, encoding="utf-8"))
    for i in d["data"]["web"]:
        print(i["title"])
        print(i["url"])
        print(i.get("description", "")[:500])
        print("---")

text = open(os.path.join(base, "wn-nagano.md"), encoding="utf-8").read()
idx = text.find("上高地")
print("==== nagano kamikochi ====")
print(text[idx : idx + 900] if idx >= 0 else "not found")
