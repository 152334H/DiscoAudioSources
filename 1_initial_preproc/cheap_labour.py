#!/usr/bin/env python3
import csv
import argparse
from json import load

parser = argparse.ArgumentParser(description="Manually label a single Actor's lines")
parser.add_argument('--actorName', metavar='name', type=str,
                    help='The name of the voice actor (e.g. Kim Kitsuragi)')
parser.add_argument('--actorID', metavar='id', type=int,
                    help='The ID of the voice actor (e.g. 395)')
parser.add_argument('outfile', metavar='outfile', type=str,
                    help='The output file')
args = parser.parse_args()
if args.actorName and args.actorID: raise RuntimeError("dont specify both")
if args.actorName:
    with open('./actors_by_narrator.json') as f:
        aID = next(actor['actorId'] for actor in load(f)
                    if actor['name'] == args.actorName)
elif args.actorID: aID = args.actorID
else: raise RuntimeError("missing args")

with open('./AudioClipMetadata.csv') as f:
    reader = csv.reader(f)
    headers = next(reader)
    inlines = [{headers[i]:v for i,v in enumerate(line)} for line in reader if int(line[-2]) == aID]

outlines = []
def save():
    from csv import writer
    with open(args.outfile, 'w') as f:
        w = writer(f)
        w.writerow(outlines[0])

outlines = []
i = len(outlines)
def add(label: str):
    outlines.append({**inlines[i], 'label': label})
while i < len(inlines):
    text = inlines[i]['text']
    ''' ADD THIS IF YOU'RE STRIPPING QUOTES
    if '"' in inlines[i]['text']:
        dialogue = text.split('"')[1::2]
        outlines.append({**inlines[i], 'text': '. '.join(dialogue)})
    '''
    outlines.append({**inlines[i], 'text': text})
    i += 1
save()
