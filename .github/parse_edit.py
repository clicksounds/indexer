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
edit_pattern = r"!edit\s+(\w+)\s+(.+)"
edits = re.findall(edit_pattern, comment_body, re.IGNORECASE)
if not edits:
    print("No !edit commands found.")
    sys.exit(0)

edit_file = Path(f"edit_commands_{issue_number}.json")
if edit_file.exists():
    with open(edit_file, "r") as f:
        data = json.load(f)
else:
    data = {}

confirmation_lines = []
for field, value in edits:
    user_value = value.strip('" ')
    try:
        parsed = json.loads(user_value)
        data[field] = parsed
        shown_value = json.dumps(parsed)
    except Exception:
        data[field] = user_value
        shown_value = user_value
    confirmation_lines.append(f'`{field}` has been set to `{shown_value}`')

with open(edit_file, "w") as f:
    json.dump(data, f, indent=2)

# Output for workflow step
confirmation = '\n'.join(confirmation_lines)
with open("edit_confirmation.txt", "w", encoding="utf-8") as f:
    f.write(confirmation)
