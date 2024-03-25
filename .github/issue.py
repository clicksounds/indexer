import json
import hashlib
import os
import sys
import zipfile
import urllib.request
import re
from pathlib import Path
import subprocess

def fail(msg):
	print(f'Fail: {msg}', file=sys.stderr)
	sys.exit(1)

def sanitize_name(name):
    # Remove any characters that are not letters, numbers, underscores, or periods
    return ((((''.join(c for c in name if c.isalnum() or c in ['.'] or c in [' '] or c in ['_'] or c in ['-']))).replace(" ", "_")).replace("-", "_")).replace(".", "_")

index_path = Path(sys.argv[1])
issue_author = sys.argv[2]
if len(sys.argv) == 3:
	issue_body = os.environ['ISSUE_BODY']
else:
	# not passing issue body as a system argument for injection reasons
	# but its still here for testing
	issue_body = sys.argv[3]


if 'Click Sound Name' not in issue_body or "Add Pack" not in issue_body:
	print('Not a valid entry', file=sys.stderr)
	sys.exit(2)

try:
	match = re.search(r'\s*?### Add Pack\s*?(\S+)\s*?', issue_body);
	match2 = re.search(r"\s*?### Your mod link\s*?(.+?)\s*?", issue_body);
	if match and match2:
		clickName = match2.group(1)
		folderName = sanitize_name(clickName)
		matchfound = match.group(1)
		click_url = matchfound[(matchfound.find("(") + 1):-1]
		print(clickName)
		print(folderName)
		print(matchfound)
		print(click_url)
		urllib.request.urlretrieve(click_url, 'test/' + folderName + '.zip')
	else:
		fail(f'Could not find the zip link')

except Exception as inst:
	fail(f'Could not download the zip file: {inst}')


try:
	archive = zipfile.ZipFile(folderName + '.zip', 'r')

	file_list = archive.namelist()
	print(file_list)

except Exception as inst:
	fail(f'Not a valid geode file: {inst}')




except Exception as inst:
	fail(f'Could not download the zip file: {inst}')

def send_webhook(mod_id):
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

	title = f'Added `{mod_id}`'
	description = 'New click added!\n' + description


	embeds = [
		{
			'color': COLOR,
			'title': title,
			'description': description,
			'thumbnail': {
				'url': f'https://raw.githubusercontent.com/geode-sdk/mods/main/mods-v2/{mod_id}/logo.png'
			}
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
		#send_webhook(mod_id)
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
		file.write(f'mod_id={mod_id}\n')