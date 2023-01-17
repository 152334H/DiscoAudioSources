#!/usr/bin/env python3
'''
#####################
 THIS FILE IS UNUSED
#####################
'''
import os
import csv
import argparse
from json import load,dump

class _GetchUnix:
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
getch = _GetchUnix()

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

if os.path.exists(args.outfile):
    with open(args.outfile) as f: outlines = load(f)
else: outlines = []

with open('./AudioClipMetadata.csv') as f:
    reader = csv.reader(f)
    headers = next(reader)
    inlines = [{headers[i]:v for i,v in enumerate(line)} for line in reader if int(line[-2]) == aID]
def save():
    with open(args.outfile, 'w') as f: dump(outlines, f)
    print('saved!')
    exit()

i = len(outlines)
def add(label: str):
    outlines.append({**inlines[i], 'label': label})
while i < len(inlines):
    print(inlines[i])
    print('1 - Quoted\n2 - Unquoted\n0 - Narrator')
    c = getch()
    if c == '0': add('Narrator')
    elif c == '1': add('Quoted')
    elif c == '2': add('Unquoted')
    elif c == '\x03': save()
    elif c == 'q':
        if 'y' in input('QUIT WITHOUT SAVING?'): exit()
        else: i -= 1
    else: add('Unknown')
    i += 1
save()
