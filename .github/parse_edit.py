import sys
import json
import re
from pathlib import Path

# Example usage:
# !edit id "author.exampleid"
# !edit name "a click pack name"
# !edit authors '["author1", "author2"]'
# !edit description "A description of the click pack"

# Usage: parse_edit.py <issue_number> <comment_body>
issue_number = sys.argv[1]
comment_body = sys.argv[2]

# Support multiple !edit commands in one comment, one per line
edit_pattern = r"!edit\\s+(\\w+)\\s+(.+)"
edits = re.findall(edit_pattern, comment_body, re.IGNORECASE)
if not edits:
    sys.exit(0)

edit_file = Path(f"edit_commands_{issue_number}.json")
if edit_file.exists():
    with open(edit_file, "r") as f:
        data = json.load(f)
else:
    data = {}

for field, value in edits:
    # Try to parse as JSON for lists/objects, else treat as string
    value = value.strip('" ')
    try:
        parsed = json.loads(value)
        data[field] = parsed
    except Exception:
        data[field] = value

with open(edit_file, "w") as f:
    json.dump(data, f, indent=2)
