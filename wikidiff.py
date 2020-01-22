#!/usr/bin/python3

import requests
import json
import re
import sys
import difflib

def printDiff(revision, format="colors"):
	session = requests.Session()
	
	url = "https://de.wikipedia.org/w/api.php"
	
	params = {
		"action": "compare",
		"format": "json",
		"fromrev": str(revision),
		"torelative": "prev",
		"prop": "diff"
	}
	
	response = session.get(url=url, params=params, stream=True)
	data = bytearray()
	for chunk in response.iter_content(chunk_size=1024):
		data += chunk	
	
	res = json.loads(data.decode('utf8'))
	
	deleteEx = r"<del .+?>(.+?)<\/del>"
	htmlEx = r"<(|\/)(td|div|a)(| .+?)>"
	
	if "compare" not in res:
		print("No content found!")
		return
		
	html = res["compare"]["*"]
	lastline = "";
	for line in html.split("\n"):
		line = line.strip()
		if line.startswith("<td class=\"diff-deletedline\">"):
			if "<del class=\"diffchange diffchange-inline\">" in line:
				if format=="termcolor":
					line = re.sub(deleteEx, "\33[31m"+"\\1"+"\033[0m", line)
				elif format=="html":
					line = re.sub(deleteEx, "<troll>\\1</troll>", line)
				elif format=="markdown":
					line = re.sub(deleteEx, "**\\1**", line)
				elif format=="plain":
					line = re.sub(deleteEx, "!!!\\1!!!", line)
				line = re.sub(htmlEx, "", line)
				if format=="html":
					line = "<troll>+</troll> "+line
					line = line+"<br>"
			else:
				line = re.sub(htmlEx, "", line)
				line = line.strip()
				if format=="termcolor":
					line = "\33[31m"+line+"\033[0m"
				elif format=="html":
					line = "<troll>"+line+"</troll><br>"
					line = "<troll>+</troll> "+line
				elif format=="markdown":
					line = "**"+line+"**"
				elif format=="plain":
					line = "!!!"+line+"!!!"
			print(line)
		if line.startswith("<td class=\"diff-addedline\">"):
			if "<ins class=\"diffchange diffchange-inline\">" in line:
				if format=="termcolor":
					line = re.sub(deleteEx, "\33[31m"+"\\1"+"\033[0m", line)
				elif format=="html":
					line = re.sub(deleteEx, "<original>\\1</original>", line)
				elif format=="markdown":
					line = re.sub(deleteEx, "**\\1**", line)
				elif format=="plain":
					line = re.sub(deleteEx, "!!!\\1!!!", line)
				line = re.sub(htmlEx, "", line)
				if format=="html":
					line = "<orginal>-</original> "+line
					line = line+"<br>"
			else:
				line = re.sub(htmlEx, "", line)
				line = line.strip()
				if format=="termcolor":
					line = "\33[31m"+line+"\033[0m"
				elif format=="html":
					line = "<original>"+line+"</original><br>"
					line = "<orginal>-</original> "+line
				elif format=="markdown":
					line = "*"+line+"*"
				elif format=="plain":
					line = "???"+line+"???"
			print(line)
		if line.startswith("<td class=\"diff-context\">"):
			line = re.sub(htmlEx, "", line)
			line = line.strip()
			if line != lastline:
				lastline = line
				if format=="html":
					line = line+"<br>"
				print(line)
