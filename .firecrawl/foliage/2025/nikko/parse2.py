import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
base = r".firecrawl/foliage/2025/nikko"
for name in ["irohazaka", "toshogu", "larch", "wn-iroha", "town"]:
    path = os.path.join(base, f"{name}.json")
    print("====", name, "====")
    if not os.path.exists(path):
        print("MISSING")
        continue
    d = json.load(open(path, encoding="utf-8"))
    for i in d["data"]["web"]:
        print(i["title"])
        print(i["url"])
        print(i.get("description", "")[:450])
        print("---")
