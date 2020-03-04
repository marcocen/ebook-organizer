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
files404 = []
api_url = "https://www.googleapis.com/books/v1"

def search_book(file):
    filename = os.path.splitext(file)[0]
    r=requests.get("{}/volumes?q={}&format=json".format(api_url, filename))
    volumes = json.loads(r.text)
    if volumes['totalItems'] == 0:
        return []
    return volumes['items'][0]['volumeInfo']

def new_filename(volumeInfo):
    title = volumeInfo['title']
    authors = str.join(', ', volumeInfo['authors'])
    published = datetime.strptime(volumeInfo['publishedDate'], '%Y-%m-%d').year
    return "{} - {} ({})".format(authors, title, published)

for file in files:
    volumeInfo = search_book(file)
    if not volumeInfo:
        files404.append(file)
        continue
    fileext = os.path.splitext(file)[1]
    newname = new_filename(volumeInfo)
    destfile = os.path.join(args.out_dir, "{}{}".format(newname,fileext))
    sourcefile = os.path.join(path, file)
    print("{} ~> {}".format(sourcefile, destfile))
    copy(sourcefile, destfile)

if files404:
    print("Couldn't find info for {} files.".format(len(files404)))
    if input("Do you want to provide alternative names to search (y/[n])? ").lower().strip() == 'y':
        for file in files404:
            newname = input("Enter an alternative filename for {}: ".format(file))
            volumeInfo = search_book(newname)
            while newname != "" and not volumeInfo:
                newname = input("Enter an alternative filename for {}: ".format(file))
                volumeInfo = search_book(newname)
            if newname == "":
                continue
            fileext = os.path.splitext(file)[1]
            newname = new_filename(volumeInfo)
            destfile = os.path.join(args.out_dir, "{}{}".format(newname,fileext))
            sourcefile = os.path.join(path, file)
            print("{} ~> {}".format(sourcefile, destfile))
            copy(sourcefile, destfile)
