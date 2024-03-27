import sys
import json
from pathlib import Path

index_path = Path(sys.argv[1])
issue_author = sys.argv[2]

config = json.load(open(index_path / "indexer-config.json", "r"))
print("Approved users:")
for user in config["approve"]:
  print(user)
      
print("YES" if issue_author in config["approve"] else "NO")
