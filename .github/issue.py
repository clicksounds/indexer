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
import shutil

AlreadyIsHere = False

def fail(msg):
    print(f'Fail: {msg}', file=sys.stderr)
    sys.exit(1)

index_path = Path(sys.argv[1])
issue_author = sys.argv[2]
folderName = "yessir"

if len(sys.argv) == 3:
    issue_body = os.environ['ISSUE_BODY']
else:
    issue_body = sys.argv[3]

def sanitize_name(name):
    return ((((''.join(c for c in name if c.isalnum() or c in ['.'] or c in [' '] or c in ['_'] or c in ['-']))).replace(" ", "_")).replace("-", "_")).replace(".", "_").replace("Clicks", "").replace("Click", "").replace("clicks", "").replace("click", "").replace("Pack", "").replace("pack", "").replace("packs", "").replace("Packs", "").replace("Releases", "").replace("Release", "").replace("releases", "").replace("release", "")

def download_zip_from_issue(issue_body, out_path):
    urls = re.findall(r'(https://github\.com/user-attachments/files/[^\s]+\.zip)', issue_body)
    if not urls:
        return False
    url = urls[0]
    try:
        urllib.request.urlretrieve(url, out_path)
        return True
    except Exception as e:
        return False

try:
    archive = None
    try:
        archive = zipfile.ZipFile('test/' + folderName + '.zip', 'r')
        archive.extractall(f'test/{folderName}') 
    except Exception as inst:
        zip_path = f'test/{folderName}.zip'
        if download_zip_from_issue(issue_body, zip_path):
            try:
                archive = zipfile.ZipFile(zip_path, 'r')
                archive.extractall(f'test/{folderName}')
            except Exception as inst2:
                raise Exception("Unable to unzip even after downloading from issue body, the file may be corrupt or invalid.")
        else:
            raise Exception("Unable to unzip, and no valid .zip URL found in issue body. Make sure the packgen.zip file was not renamed and is attached.")
    
    file_list = archive.namelist()
    packjson = {}
    for x in file_list:
        if x.endswith("pack.json"):
            packjson = json.loads(archive.open(x, 'r').read().decode('utf-8'))
            clickName = packjson["name"]
            clickType = packjson.get("type", "Missing Key")

            if clickType.title() == "Meme":
                clickType = "Meme"
            elif clickType.title() == "Useful":
                clickType = "Useful"
            else:
                if clickType == "Missing Key":
                    raise Exception("Type Key is missing or invalid")
                else:
                    raise Exception('Click type: "' + str(clickType) + '" Is not a valid click type, Meme or Useful are the only valid types')

            id2 = re.search(r'^([a-z0-9\-]+\.[a-z0-9\-_]+)$', packjson["id"])
            try:
                modid = id2.group(1)
            except Exception as inst:
                raise Exception("CLICK ID presented is not valid, You may have used a invalid char")
            break

except Exception as inst:
    fail(f'Not a valid pack file: {inst}')

def send_webhook():
    from urllib import request
    import json
    import os

    COLOR = 0x8d73ce

    issue_author = os.getenv('ISSUE_AUTHOR', '?')
    comment_author = os.getenv('COMMENT_AUTHOR', '?')
    if comment_author == issue_author:
        description = f'''
Uploaded by: [{issue_author}](https://github.com/{issue_author})'''
    else:
        description = f'''
Uploaded by: [{issue_author}](https://github.com/{issue_author})
Accepted by: [{comment_author}](https://github.com/{comment_author})'''

    if (AlreadyIsHere):
        title = f'Updated `{clickName}` Click Sound'
        description = 'Updated ' + clickType + ' Sound ' + clickName + '!\n' + description
    else:
        title = f'Added `{clickName}` Click Sound'
        description = 'New ' + clickType + ' Sound ' + clickName + '!\n' + description

    embeds = [
        {
            'color': COLOR,
            'title': title,
            'description': description,
        }
    ]

    req = request.Request(os.getenv('DISCORD_WEBHOOK_URL'), method='POST')
    req.add_header('User-Agent', 'python urllib')
    req.add_header('Content-Type', 'application/json')
    data = {
        'content': None,
        'embeds': embeds,
    }
    request.urlopen(req, data=json.dumps(data).encode('utf-8'))

MaxFileCountClicks = 0
MaxFileCountReleases = 0

try:
    if clickType != "Meme" and clickType != "Useful":
        version_click_directory = modid
        raise Exception(f"Click is not a valid Clicktype (Meme || Useful are valid clicktypes)")

    mod_directory = index_path / clickType
    version_click_directory = mod_directory / modid

    if os.path.exists(version_click_directory):
        AlreadyIsHere = True

    version_click_directory.mkdir(parents=True, exist_ok=True)
    clicks_folder = version_click_directory / "Clicks"
    releases_folder = version_click_directory / "Releases"
    clicks_folder.mkdir(parents=True, exist_ok=True)
    releases_folder.mkdir(parents=True, exist_ok=True)

    for x in file_list:
        if not x.endswith("Clicks/") and not x.endswith("clicks/") and not x.endswith("Releases/") and not x.endswith("releases/") and not x.endswith("Release/") and not x.endswith("release/"):
            filename = x.split("/")
            filename = filename[len(filename) - 1]
            listdir = x.split("/")
            listdir.pop(len(listdir) - 1)
            if "Clicks" in listdir or "clicks" in listdir or "click" in listdir or "Click" in listdir:
                shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(clicks_folder, filename))
                MaxFileCountClicks += 1
            if "Releases" in listdir or "releases" in listdir or "release" in listdir or "Release" in listdir:
                MaxFileCountReleases += 1
                shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(releases_folder, filename))
        if x.endswith("pack.json"):
            filename = x.split("/")
            filename = filename[len(filename) - 1]
            shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(version_click_directory, filename))

except Exception as inst:
    fail(f'Could not populate pack folder {version_click_directory}: {inst}')

potential_issues = []
if potential_issues:
    print('## Potential issues')
    print('\n'.join(f'* {x}' for x in potential_issues))

    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as file:
            file.write('has_issues=YES\n')

try:
    if packjson and modid:
        msg = ""
        development = ""
        packgenStatus = ""
        packconStatus = ""

        if (MaxFileCountClicks > 0):
            msg = f"There are {MaxFileCountClicks} clicks"

        if (MaxFileCountReleases > 0):
            if msg != "":
                msg = msg + f" and {MaxFileCountReleases} releases"
            else:
                msg = f"There are {MaxFileCountReleases} releases"

        development = "by "
        for x in packjson["authors"]:
            if development != "by ":
                development = development + ", " + x.get("name", "Unknown")
            else:
                development = development + x.get("name", "Unknown")

        if development == "by ":
            development = "by unknown"

        if packjson.get("packgen", False):
            packgenStatus = "Packgen was used. "
        else:
            packgenStatus = "Packgen was not used. "

        if packjson.get("packcon", False):
            packconStatus = "Packcon was used to convert this pack from ZCB format to CS format. "

        packType = f'Pack type is {packjson.get("type", "Unknown").capitalize()}.'

        if (msg != ""):
            packDesc = f'\nPack description: {packjson["description"]}' if "description" in packjson else ""
            print(f'{packjson["name"]} ({modid}) {development} is waiting for an index moderator to accept the submission.\n{msg}. {packgenStatus}{packconStatus}{packType}{packDesc}')
        else:
            print(f'{packjson["name"]} ({modid}) {development} doesn\'t seem to have any click files?')
finally:
    a = ""  # ok why did python hate me

try:
    if (os.getenv('ACTUALLY_ACCEPTING') == 'YES' or not potential_issues) and os.getenv('VERIFY_USER_RESULT') == 'YES':
        send_webhook()
    else:
        with open('silly_log.txt', 'a') as file:
            file.write("not sending webhook :P\n")
except Exception as e:
    with open('silly_log.txt', 'a') as file:
        file.write(str(e) + "\n")

if os.getenv('GITHUB_OUTPUT'):
    with open(os.getenv('GITHUB_OUTPUT'), 'a') as file:
        file.write(f'mod_id={clickName}\n')
