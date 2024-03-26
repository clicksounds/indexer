import json
import hashlib
import os
import sys
import zipfile
import urllib.request
import re
from pathlib import Path
import subprocess
import time

def fail(msg):
    print(f'Fail: {msg}', file=sys.stderr)
    sys.exit(1)

def sanitize_name(name):
    return ((((''.join(c for c in name if c.isalnum() or c in ['.'] or c in [' '] or c in ['_'] or c in ['-']))).replace(" ", "_")).replace("-", "_")).replace(".", "_").replace("Clicks", "")

def save(clickName, folderName, ee):
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as file:
            file.write(f'click_name={clickName}\nfolder_name={folderName}\ntype={ee}\n')

issue_body = os.environ['ISSUE_BODY']

if 'Click Sound Name' not in issue_body or "Add Pack" not in issue_body:
    print('Not a valid entry', file=sys.stderr)
    sys.exit(2)

try:
    match = re.search(r'\s*?### Add Pack\s*?(\S+)\s*?', issue_body)
    match3 = re.search(r'\s*?### Type of Click Sound\s*?(\S+)\s*?', issue_body)
    match2 = re.search(r'### Click Sound Name\s\s(.+)', issue_body)
    time.sleep(2)
    if match and match2 and match3:
        clickName = match2.group(1)
        folderName = sanitize_name(clickName)
        matchfound = match.group(1)
        click_url = matchfound[(matchfound.find("(") + 1):-1]
        typee = match3.group(1)
        if typee != "Useful" and typee != "Meme":
            print('Click Type must be \"Useful\" or \"Release\"', file=sys.stderr)
            sys.exit(2)
        save(clickName, folderName, typee)
        urllib.request.urlretrieve(click_url, 'test/' + folderName + '.zip')
    else:
        fail(f'Could not find the zip link')

except Exception as inst:
    fail(f'Could not download the zip file: {inst}')
