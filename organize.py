#!/usr/bin/env python3
import os
import requests
import json
import argparse
from shutil import copy

from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--in-dir",
                    help="Directory where the unorganized books are located",
                    required=True)
parser.add_argument("-o", "--out-dir",
                    help="Directory where the books will be organized",
                    required=True)
parser.add_argument("-s", "--subdirs",
                    help="Organize books in subdirectories",
                    action='store_true')
args = parser.parse_args()

path = args.in_dir

files = os.listdir(path)

api_url = "https://www.googleapis.com/books/v1"
for file in files:
    print(file)
    filename = os.path.splitext(file)[0]
    fileext = os.path.splitext(file)[1]
    r=requests.get("{}/volumes?q={}&format=json".format(api_url, filename))
    volumes = json.loads(r.text)

    new_filename = "not_empty"
    while new_filename != "" and volumes['totalItems'] == 0:
        new_filename = input("No book was found for this filemane: {} input an alternative username if you want to: ".format(filename))
        if new_filename != "":
            r=requests.get("{}/volumes?q={}&format=json".format(api_url, new_filename))
            volumes = json.loads(r.text)

    if volumes['totalItems'] == 0:
        continue
    volumeInfo = volumes['items'][0]['volumeInfo']
    title = volumeInfo['title']
    authors = str.join(', ', volumeInfo['authors'])
    published = datetime.strptime(volumeInfo['publishedDate'], '%Y-%m-%d').year
    print("Title: {}".format(title))
    print("Authors: {}".format(authors))
    print("Published: {}".format(published))
    newtitle = "{} - {} ({})".format(authors, title, published)
    sourcefile = os.path.join(path, file)
    destfile = os.path.join(args.out_dir, "{}{}".format(newtitle, fileext))
    copy(sourcefile, destfile)
