#!/usr/bin/python3

import requests
import json
import sys
import os
from optparse import OptionParser
import wikidiff

parser = OptionParser("usage: %prog [options] article-title")
parser.add_option("-f", "--format", default="termcolor", action="store", dest="format", help="specify output format: [termcolor] html markdown plain")

(options, args) = parser.parse_args()
format = options.format

if len(args) != 1:
	parser.error("incorrect number of arguments")

session = requests.Session()

url = "https://de.wikipedia.org/w/api.php"

params = {
	"action": "query",
	"format": "json",
	"prop": "revisions|info",
	"titles": args[0],
	"rvprop": "ids|timestamp|comment",
	"rvslots": "main",
	"rvlimit": "max"
}

first = True
while True:
	response = session.get(url=url, params=params, stream=True)
	data = bytearray()
	for chunk in response.iter_content(chunk_size=1024):
		data += chunk	

	res = json.loads(data.decode('utf8'))
	page = list(res["query"]["pages"].values())[0]

	if "missing" in page:
		print("Cannot find page: "+page["title"], file=sys.stderr)
		sys.exit(2)
		
	if first:
		if format=="termcolor":
			print("\33[1m"+"\33[4m"+page["title"]+"\033[0m")
		if format=="markdown":
			print("# "+page["title"])
		if format=="html":
			print("<h1>"+page["title"]+"</h1>")
		if format=="plain":
			print("#---------------------------"+page["title"]+"---------------------------#")
		first = False

	revisions = page["revisions"]
	for revision in revisions:
		if "comment" in revision:
			comment = revision["comment"]
			if "Änderungen von" in comment and "zurückgesetzt" in comment:
				revid=revision["revid"]
				if format=="plain":
					print("----------------------------"+str(revid)+"----------------------------")
				if format=="termcolor":
					print("\33[4m"+str(revid)+"\033[0m")
				elif format=="html":
					print("<h2>"+str(revid)+"</h2>")
				elif format=="markdown":
					print("## "+str(revid))
				wikidiff.printDiff(revid, format)
	
	lastrev = revisions[len(revisions)-1]
	if lastrev["parentid"] != 0:
		params["rvstartid"] = lastrev["parentid"]
	else:
		break

