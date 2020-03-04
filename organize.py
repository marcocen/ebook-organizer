#!/usr/bin/env python3
import os
import requests
import json
import argparse
from shutil import copy
from dateutil.parser import parse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--in-dir",
                    help="Directory where the unorganized books are located",
                    required=True)
parser.add_argument("-o", "--out-dir",
                    help="Directory where the books will be organized",
                    required=True)
parser.add_argument("-t", "--template",
                    help="Template for the filename",
                    default="%a - %t (%y)")
args = parser.parse_args()

path = args.in_dir
outdir = args.out_dir
files = os.listdir(path)
files404 = []
api_url = "https://www.googleapis.com/books/v1"
template = args.template

template_vars = {
    '%a': 'author',
    '%t': 'title',
    '%y': 'year',
    '%s': 'subtitle',
    '%p': 'publisher',
    '%i': 'isbn'
}

def search_book(file):
    filename = os.path.splitext(file)[0]
    r=requests.get("{}/volumes?q={}&format=json".format(api_url, filename))
    volumes = json.loads(r.text)
    if volumes['totalItems'] == 0:
        return []
    return volumes['items'][0]['volumeInfo']

def new_filename(volumeInfo, fileExt, template):
    volumeInfo['year'] = str(parse(volumeInfo['publishedDate']).year)
    volumeInfo['isbn'] = list(filter(lambda x: x['type']=="ISBN_13", volumeInfo["industryIdentifiers"]))[0]['identifier']
    volumeInfo['author'] = str.join(', ', volumeInfo['authors'])
    title = template
    for k,v in template_vars.items():
        if v in volumeInfo.keys():
            title = title.replace(k, volumeInfo[v])
        else:
            title = title.replace(k, "")
    return "{}{}".format(title, fileExt)

def archive_file(sourceFile, destFile):
    print("{} ~> {}".format(sourcefile, destfile))
    if not os.path.isdir(os.path.dirname(destfile)):
        os.mkdir(os.path.dirname(destfile))
    copy(sourcefile, destfile)

def file_is_ebook(file):
    formats = [
        '.pdf',
        '.epub',
        '.mobi',
        '.azw',
        '.azw3',
        '.iba',
        '.djvu',
        '.rtf'
    ]
    return os.path.splitext(file)[1].lower() in formats

for file in files:
    if not file_is_ebook(file):
        continue
    fileext = os.path.splitext(file)[1]
    volumeInfo = search_book(file)
    if not volumeInfo:
        files404.append(file)
        continue
    destfile = os.path.join(outdir, new_filename(volumeInfo, fileext, args.template))
    sourcefile = os.path.join(path, file)
    archive_file(sourcefile, destfile)

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
            destfile = os.path.join(outdir, new_filename(volumeInfo, fileext, args.template))
            sourcefile = os.path.join(path, file)
            archive_file(sourcefile, destfile)
