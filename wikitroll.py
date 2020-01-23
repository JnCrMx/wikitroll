#!/usr/bin/python3

import requests
import json
import sys
import os
from optparse import OptionParser
import wikidiff
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

parser = OptionParser("usage: %prog [options] article-title")
parser.add_option("-f", "--format", default="html", action="store", dest="format", help="specify output format: termcolor [html] markdown plain")
parser.add_option("-l", "--language", default="de", action="store", dest="lang", help="specify Wikipedia language to query")

(options, args) = parser.parse_args()
format = options.format
lang = options.lang

if len(args) != 1:
	parser.error("incorrect number of arguments")

session = requests.Session()

languages = { }

languages["de"] = {}
languages["de"]["url"] = "https://de.wikipedia.org/w/api.php"
languages["de"]["comment"] = ["Änderungen von", "zurückgesetzt"]

languages["en"] = {}
languages["en"]["url"] = "https://en.wikipedia.org/w/api.php"
languages["en"]["comment"] = ["Reverted", "edit", "to last revision by"]

params = {
	"action": "query",
	"format": "json",
	"prop": "revisions|info",
	"titles": args[0],
	"rvprop": "ids|timestamp|comment",
	"rvslots": "main",
	"rvlimit": "max"
}

dateformat = "%Y-%m-%dT%H:%M:%SZ"

first = True
while True:
	response = session.get(url=languages[lang]["url"], params=params, stream=True)
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
			print("<html>")
			print("<head>")
			print("<title>"+page["title"]+"</title>")
			print("<style>")
			print("troll { color: red }")
			print("original { color: green }")
			print(".tp { border: 2px solid red; padding: 5px; margin: 5px; }")
			print(".op { border: 2px solid green; padding: 5px; margin: 5px; }")
			print(".cp { border: 2px solid black; padding: 5px; margin: 5px; }")
			print("</style>")
			print("</head>")
			print("<body>")
			print("<h1>"+page["title"]+"</h1>")
		if format=="plain":
			print("#---------------------------"+page["title"]+"---------------------------#")
		first = False

	revisions = page["revisions"]
	for revision in revisions:
		if "comment" in revision:
			comment = revision["comment"]
			istroll = all(ele in comment for ele in languages[lang]["comment"])
			if istroll:
				revid=revision["revid"]
				time=revision["timestamp"]
				time=str(datetime.strptime(time, dateformat))
				if format=="plain":
					print("----------------------------"+str(revid)+" @ "+time+"----------------------------")
				if format=="termcolor":
					print("\33[4m"+str(revid)+"\033[0m"+" @ "+time)
				elif format=="html":
					print("<hr>")
					print("<h2>"+str(revid)+"</h2>")
					print("<h3>"+time+"</h3>")
				elif format=="markdown":
					print("## "+str(revid))
					print("### "+time)
				wikidiff.printDiff(revid, languages[lang]["url"], format)
	
	lastrev = revisions[len(revisions)-1]
	if lastrev["parentid"] != 0:
		params["rvstartid"] = lastrev["parentid"]
	else:
		break

if format=="html":
	print("</body>")
	print("</html>")
