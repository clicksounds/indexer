import sys
import json
from pathlib import Path
try:
    index_path = Path(sys.argv[1])
    issue_author = sys.argv[2]

    config = json.load(open(index_path / "indexer-config.json", "r"))
    print("YES" if issue_author in config["approve"] else "NO")
except Exception as e:
    print(f"Error: {e}")
