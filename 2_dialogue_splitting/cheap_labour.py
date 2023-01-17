#!/usr/bin/env python3
import csv
import argparse
from json import load

### argument definitions
parser = argparse.ArgumentParser(description="Extract lines for a single Actor that were not spoken by the Narrator.")
parser.add_argument('--actorName', metavar='name', type=str,
                    help='The name of the voice actor (e.g. Kim Kitsuragi)')
parser.add_argument('--actorID', metavar='id', type=int,
                    help='The ID of the voice actor (e.g. 395)')
parser.add_argument('outfile', metavar='outfile', type=str,
                    help='The output file')
args = parser.parse_args()

### argument validation
if args.actorName and args.actorID: raise RuntimeError("dont specify both")
if args.actorName:
    with open('./actors_by_narrator.json') as f:
        aID = next(actor['actorId'] for actor in load(f)
                    if actor['name'] == args.actorName)
elif args.actorID: aID = args.actorID
else: raise RuntimeError("missing args")

## loading lines by actor from preproc
with open('../1_initial_preproc/AudioClipMetadata.csv') as f:
    reader = csv.reader(f)
    headers = next(reader)
    inlines = [{headers[i]:v for i,v in enumerate(line)} for line in reader if int(line[-2]) == aID]
    print(inlines[:10])

## predefine function to save output
outlines = []
def save():
    print(outlines[:10])
    from csv import writer
    with open(args.outfile, 'w') as f:
        w = writer(f)
        w.writerow(outlines[0])
        w.writerows((d.values() for d in outlines))

### process input lines
STRIP_QUOTES = True
for i in range(len(inlines)):
    text = inlines[i]['text']
    if not STRIP_QUOTES:
        outlines.append({**inlines[i], 'text': text})
    elif '"' in inlines[i]['text']:
        dialogue = text.split('"')[1::2]
        outlines.append({**inlines[i], 'text': '. '.join(dialogue)})
    else: print("IGNORING:", text)

## save output
save()
