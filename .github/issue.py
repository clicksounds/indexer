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

def fail(msg):
	print(f'Fail: {msg}', file=sys.stderr)
	sys.exit(1)


index_path = Path(sys.argv[1])
issue_author = sys.argv[2]
clickName = os.environ['CLICK_NAME']
clickType = os.environ['CLICK_TYPE']
folderName = os.environ['FOLDER_NAME']
if len(sys.argv) == 3:
	issue_body = os.environ['ISSUE_BODY']
else:
	# not passing issue body as a system argument for injection reasons
	# but its still here for testing
	issue_body = sys.argv[3]


try:
	archive = zipfile.ZipFile('test/' + folderName + '.zip', 'r')

	file_list = archive.namelist()
	print(file_list)

except Exception as inst:
	fail(f'Not a valid geode file: {inst}')




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
	title = f'Added New {clickType} Sound, `{clickName}`'
	description = 'New click added!\n' + description


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
	version_mod_directory = mod_directory / folderName
	print(folderName)
	print(mod_directory)
	print(version_mod_directory)
	version_mod_directory.mkdir(parents=True, exist_ok=False)
	clicks_folder = version_mod_directory / "Clicks"
	releases_folder = version_mod_directory / "Releases"
	clicks_folder.mkdir(parents=True, exist_ok=True)
	releases_folder.mkdir(parents=True, exist_ok=True)

	for x in file_list:
		if x != "Clicks/" and x != "clicks/" and x != "Releases/" and x != "releases/" and x != "Release/" and x != "release/":
			filename = x.split("/")
			filename = filename[len(filename) - 1]
			listdir = x.split("/")
			listdir.pop(len(listdir) - 1)
			if "Clicks" in listdir or "clicks" in listdir or "click" in listdir or "Click" in listdir:
				print(x)
				print(os.path.join(os.path.join("test/", folderName), x))
				print(os.path.join(clicks_folder, filename))
				shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(clicks_folder, filename))
			if "Releases" in listdir or "releases" in listdir or "release" in listdir or "Release" in listdir:
				shutil.copy(os.path.join(os.path.join("test/", folderName), x), os.path.join(releases_folder, filename))

except Exception as inst:
	fail(f'Could not populate click folder {version_mod_directory}: {inst}')

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
		print("hello")
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
