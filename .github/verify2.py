import sys
import json
from pathlib import Path

index_path = Path(sys.argv[1])
issue_author = sys.argv[2]

config = json.load(open(index_path / "indexer-config.json", "r"))
# Function to recursively convert all string values to lowercase
def lowercase_strings(value):
    if isinstance(value, dict):
        return {k: lowercase_strings(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [lowercase_strings(item) for item in value]
    elif isinstance(value, str):
        return value.lower()
    else:
        return value

print("YES" if issue_author.lower() in lowercase_strings(config["approve"]) else "NO")
