from typing import Dict
from dataset_creator import DatasetCreator
def create_line(args: Dict[str,str]):
    return f'wavs/{args["fname"]}|{args["text"]}'

with open('./BEST_LINES.txt') as f:
    whitelist = {l.split('|')[0][5:] for l in f.readlines()}

DatasetCreator(create_line, outfile='./TalkNetDataset/metadata.txt', wav_dst='./TalkNetDataset/wavs/', whitelist=whitelist, split=True)

