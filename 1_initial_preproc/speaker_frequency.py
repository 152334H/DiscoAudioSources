#!/usr/bin/env python3
import csv
from json import load
from collections import defaultdict

d = defaultdict(int)
nt = set()
with open('./actors_by_narrator.json') as f:
    for actor in load(f):
        if actor['narratorType'] == 'Narrator':
            nt.add(actor['actorId'])

with open('./AudioClipMetadata.csv') as f:
    reader = csv.reader(f)
    headers = next(reader)
    inlines = [{headers[i]:v for i,v in enumerate(line)} for line in reader]
    for l in inlines:
        if int(l['actorID']) not in nt:
            d[l['actorName']] += 1
for l in sorted((v,k) for k,v in d.items()):
    print(l)
