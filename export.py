#!/bin/env python3
import requests
import json
from os.path import exists
import os
import uuid
import dateutil.parser
import time

headers = { 
    "Accept" : "aplication/json, text/plain, */*",
    "Accept-Encoding" : "gzip, deflate, br",
    "Accept-Language" : "en-US,en;q=0.9,es;q=0.8",
    "Authorization"  : "", # add your authorization token here (i.e. OAuth deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef)
    "Cache-Control" : "no-cache",
    "Connection" :  "keep-alive",
    "Content-Type" : "application/json;charset=UTF-8",
    "dnt"  :"1",
    "Expires" :  "Sat, 01 Jan 2000 00:00:00 GMT",
    "Host"  : "duge.neat.com",
    "Origin"  : "https://app.neat.com",
    "Pragma"  : "no-cache",
    "Referer" :  "https://app.neat.com/",
    "Sec-Fetch" : "Dest: empty",
    "Sec-Fetch" : "Mode: cors",
    "Sec-Fetch" : "Site: same-site",
    "Sec-GPC" : "1",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.35 Safari/537.36",
    "x-neataccount-id" : "" # add your account id here (i.e. deadbeefdeadbeefdeadbee)
}
folderReqestPayload = {
    "page":1,"page_size":50
    }

itemRequestUrl = "https://duge.neat.com/cloud/items"

# list items of a folder and then recurse into subfolders
def enumerateFolder(folderid, currentFolder) :
    # if folder doesn't exist, make it and drop in files
    # if it existed, enumerate subs but don't drop in items
    if not exists(currentFolder):
        os.mkdir(currentFolder)
        getItems(folderid, currentFolder)

    # now get the folder listing and enumerate through each one
    url = "https://duge.neat.com/cloud/folders/" +folderid+"/subfolders"
    r = requests.post(url, headers=headers, json=folderReqestPayload)
    res = json.loads(r.text)
    entities = res["entities"]
    for ent in entities:
        print(f"Name: {ent['name']}, id: {ent['webid']}")
        subFolder = os.path.join(currentFolder, ent["name"])
        enumerateFolder(ent["webid"], subFolder)

def getItems(folderid, currentFolder):
    itemNbr = 0
    totalItems = -1
    page = 1
    url = itemRequestUrl

    while itemNbr != totalItems:
        itemRequestPayload = {
            "filters": [ { "parent_id": folderid }, { "type":"$all_item_types"}],
            "page": page,
            "page_size":"100",
            "sort_by":[["created_at","desc"]],
            "utc_offset":-5
        }
        r = requests.post(url, headers=headers, json=itemRequestPayload)
        res = json.loads(r.text)
        entities = res["entities"]
        pagination = res["pagination"]
        if totalItems == -1:
            totalItems = pagination["total_records"]
        # download items
        for item in entities:
            itemNbr += 1
            downloadUrl = item["download_url"]
            if downloadUrl is None:
                print(f"{itemNbr} Created: {item['created_at']}, download: None available")
                continue
            print(f"{itemNbr} Created: {item['created_at']}, download: {downloadUrl[-10:]}")
            download = requests.get(downloadUrl)
            fileName = os.path.join(currentFolder, uuid.uuid4().hex) + ".pdf"
            # save file to disk
            with open(fileName, "wb") as file:
                file.write(download.content)
            # update date/time
            fileDate = dateutil.parser.isoparse(item["created_at"])
            fileDateTuple = time.mktime(fileDate.timetuple())
            os.utime(fileName, (fileDateTuple, fileDateTuple))
        # increment page count for next page
        page += 1




enumerateFolder(myroot, parentFolder)
print("Done")