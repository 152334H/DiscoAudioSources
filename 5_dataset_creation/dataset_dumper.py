import os
import csv
import librosa
import soundfile
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
from pathlib import Path
from shutil import copy
from typing import List,Optional,Dict,Set,Any,Callable, Tuple
from json import load
from multiprocessing import Pool
from functools import partial

WAV_SRC = '../0_original_data/AudioClip/'
CSV_SRC='../1_initial_preproc/AudioClipMetadata.csv'
OUTDIR = Path('../final_dataset/')

with open('../1_initial_preproc/actors_by_narrator.json') as f:
    df_actor = pd.json_normalize(load(f))

def split_file(src, train, test, per=0.80):
    import random
    with open(src) as f:
        lines = f.readlines()
    random.shuffle(lines)
    idx = int(len(lines)*per)
    with open(train, 'w') as f: f.write(''.join(lines[:idx]))
    with open(test, 'w') as f: f.write(''.join(lines[idx:]))

def create_line(args: Dict[str,str]):
    return f'wavs/{args["fname"]}|{args["text"]}'

def reject_null(args): return args
def reject_kk(args: Dict[str,str]):
    if 'COALITION WARSHIP ARCHER' in args['fname']: return
    return args
FILTERS = defaultdict(lambda: reject_null, {
    395: reject_kk
})


KEYS = ['fname', 'acticyID', 'alternativeIdx', 'text', 'actorID', 'actorName']
def line_filter(line: List[str]) -> Optional[Dict[str,str]]:
    fname, text, actorID = line[0], line[3], int(line[4])
    filt = FILTERS[actorID]
    actor = df_actor.loc[int(actorID)-1]
    assert actor.actorId == int(actorID)
    if not text.isascii(): return
    if len(text) not in range(6,150): return # token bounds
    # TODO: handle asterisks
    # TODO: fix e.g. "51 - 8 = 42"
    text = text.replace(' --> ', ', ').replace(' -- ', ', ').replace(' - ', ', ').replace('=', 'equals').replace('&', 'and').replace('\n', '. ').replace('*','')
    #
    args = {KEYS[i]:s for i,s in enumerate(line)}
    args['actor'] = actor
    args['text'] = text
    if actor.narratorType == 'Narrator':
        args['name'] = "Narrator"
    elif actor.narratorType != 'NPC' or '"' not in text:
        return None
    else:
        args['name'] = args['actor']['name']
        dialogue = text.split('"')[1::2]
        args['text'] = '. '.join(dialogue)
    args['basedir'] = OUTDIR/args['name'] # pyright: ignore
    return filt(args)

def consider(line: List[str]) -> Optional[Tuple[Path,str]]:
    if (args := line_filter(line)):
        fname = args['fname']
        assert isinstance(args['basedir'],Path)
        src,dst = WAV_SRC+fname, args['basedir'].joinpath('wavs',fname)
        dst.parent.mkdir(parents=True, exist_ok=True)
        copy(src, dst) # very slow operation.
        return args['basedir']/'metadata.txt', create_line(args)

def run():
    CORES,BS = 8,1<<6
    with open(CSV_SRC) as csvfile: row_count = sum(1 for _ in csv.reader(csvfile))
    all_lines: Dict[Path,list] = defaultdict(list)
    with open(CSV_SRC) as csvfile, Pool(CORES) as pool:
        reader = csv.reader(csvfile)
        next(reader) # ignore header
        for outfile,line in tqdm(
            filter(None,
                pool.imap(consider, reader, BS),
            ), total=row_count-1
        ):
            all_lines[outfile].append(line)
    for outfile,lines in all_lines.items():
        outfile.write_text('\n'.join(lines))
        split_file(
            outfile,
            outfile.with_suffix(".train.txt"),
            outfile.with_suffix(".test.txt")
        )

if any(not os.path.exists(d) for d in [WAV_SRC, CSV_SRC]):
    raise FileNotFoundError
run()

