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
	# not passing issue body as a system argument for injection reasons
	# but its still here for testing
	issue_body = sys.argv[3]

def sanitize_name(name):
    return   ((((''.join(c for c in name if c.isalnum() or c in ['.'] or c in [' '] or c in ['_'] or c in ['-']))).replace(" ", "_")).replace("-", "_")).replace(".", "_").replace("Clicks", "").replace("Click","").replace("clicks", "").replace("click","").replace("Pack", "").replace("pack","").replace("packs", "").replace("Packs","").replace("Releases", "").replace("Release","").replace("releases", "").replace("release","") 

try:
	archive = zipfile.ZipFile('test/' + folderName + '.zip', 'r')
	file_list = archive.namelist()
	packjson = {}
	for x in file_list:
		if x.endswith("pack.json"):
			print(archive.open(x, 'r').read().decode('utf-8'))
			packjson = json.loads(archive.open(x, 'r').read().decode('utf-8'))
	print(file_list)
	clickName = packjson["name"]
	id2 = re.search(r'^([a-z0-9\-]+\.[a-z0-9\-]+)$', packjson["id"])
	modid = id2.group(1)
    

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

	# if some
	if (AlreadyIsHere):
		title = f'Updated `{clickName}` Click Sound'
		description = 'Updated '+clickType+' Sound '+clickName+'!\n' + description
	else:
		title = f'Added `{clickName}` Click Sound'
		description = 'New '+clickType+' Sound '+clickName+'!\n' + description
	

	embeds = [
		{
			'color': COLOR,
			'title': title,
			'description': description,
			#'thumbnail': {
			#	'url': f'https://raw.githubusercontent.com/geode-sdk/mods/main/mods-v2/{mod_id}/logo.png'
			#}
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

try:
	mod_directory = index_path / clickType
	version_click_directory = mod_directory / modid
	#print(folderName)
	#print(mod_directory)
	#print(version_mod_directory)
	if os.path.exists(version_mod_directory):
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
				#print(x)
				#print(os.path.join(os.path.join("test/", folderName), x))
				#print(os.path.join(clicks_folder, filename))
				shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(clicks_folder, filename))
			if "Releases" in listdir or "releases" in listdir or "release" in listdir or "Release" in listdir:
				shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(releases_folder, filename))
		if x.endswith("pack.json"):
			filename = x.split("/")
			filename = filename[len(filename) - 1]
			shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(version_mod_directory, filename))

except Exception as inst:
	fail(f'Could not populate pack folder {version_mod_directory}: {inst}')

potential_issues = []
if potential_issues:
	print('## Potential issues')
	print('\n'.join(f'* {x}' for x in potential_issues))

	if os.getenv('GITHUB_OUTPUT'):
		with open(os.getenv('GITHUB_OUTPUT'), 'a') as file:
			file.write('has_issues=YES\n')


# mod only gets auto accepted when there are no issues
try:
	# ignore potential issues if this is triggered by a staff !accept command
	if (os.getenv('ACTUALLY_ACCEPTING') == 'YES' or not potential_issues) and os.getenv('VERIFY_USER_RESULT') == 'YES':
		send_webhook()
	else:
		with open('silly_log.txt', 'a') as file:
			file.write("not sending webhook :P\n")
except Exception as e:
	# dont care about webhook failing
	with open('silly_log.txt', 'a') as file:
		file.write(str(e) + "\n")

if os.getenv('GITHUB_OUTPUT'):
	with open(os.getenv('GITHUB_OUTPUT'), 'a') as file:
		file.write(f'mod_id={clickName}\n')
