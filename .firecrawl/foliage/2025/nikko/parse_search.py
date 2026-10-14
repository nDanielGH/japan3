import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
base = r".firecrawl/foliage/2025/nikko"
for name in ["jg-search", "jp-search", "yellow-search", "red-search", "wn-search"]:
    path = os.path.join(base, f"{name}.json")
    print("====", name, "====")
    d = json.load(open(path, encoding="utf-8"))
    for i in d["data"]["web"]:
        print(i["title"])
        print(i["url"])
        print(i.get("description", "")[:450])
        print("---")
