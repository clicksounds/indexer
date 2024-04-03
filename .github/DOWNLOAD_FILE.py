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
    print(f'Fail: {msg}')
    print(f'Fail: {msg}', file=sys.stderr)
    sys.exit(1)


def save(folderName):
    print(folderName)
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as file:
            file.write(f'folder={folderName}\n')

issue_body = os.environ['ISSUE_BODY'].replace("\r", "")

if "Add Pack" not in issue_body:
    print('Not a valid entry', file=sys.stderr)
    sys.exit(2)

try:
    match = re.search(r'\s*?### Add Pack\s*?(\S+)\s*?', issue_body)
    print(match)
    time.sleep(2)
    if match:
        matchfound = match.group(1)
        click_url = matchfound[(matchfound.find("(") + 1):-1]
        urllib.request.urlretrieve(click_url, 'test/' + 'yessir' + '.zip')
        folderName = "yessir"
        print(matchfound)
        save(folderName)
    else:
        fail(f'Could not find the zip link')

except Exception as inst:
    fail(f'Could not download the zip file: {inst}')
