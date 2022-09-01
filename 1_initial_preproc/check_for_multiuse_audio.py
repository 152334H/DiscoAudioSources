#!/usr/bin/env python3
import csv
from collections import defaultdict
cnt = defaultdict(list)
with open('./AudioClipMetadata.csv') as f:
    reader = csv.reader(f)
    headers = next(reader)
    #print(headers)
    for line in reader:
        d = {headers[i]:v for i,v in enumerate(line)}
        cnt[d['fname']].append(d)
for k,v in cnt.items():
    if len(v) > 1:
        print(k)
        for d in v:
            print('\t', d['acticyID'], d['text'])
        print('-'*80)

