import os
import csv
import librosa
import soundfile
from tqdm import tqdm
from pathlib import Path
from shutil import copy
from typing import List,Optional,Dict,Set,Any,Callable
from multiprocessing import Pool
from functools import partial


def split_file(src, train, test, per=0.80):
    import random
    with open(src) as f:
        lines = f.readlines()
    random.shuffle(lines)
    idx = int(len(lines)*per)
    with open(train, 'w') as f: f.write(''.join(lines[:idx]))
    with open(test, 'w') as f: f.write(''.join(lines[idx:]))

class DatasetCreator:
    # Interface for impl

    KEYS = ['fname', 'acticyID', 'alternativeIdx', 'text', 'actorID', 'actorName']
    @staticmethod
    def filter(line: List[str], whitelist: Optional[Set[str]], apply_filter: Optional[Callable]) -> Optional[Dict[str,str]]:
        fname, text = line[0], line[3]
        if whitelist and fname not in whitelist: return
        # TODO: handle asterisks
        if not text.isascii(): return
        if len(text) not in range(6,150): return # token bounds
        # TODO: fix e.g. "51 - 8 = 42"
        text = text.replace(' --> ', ', ').replace(' -- ', ', ').replace(' - ', ', ').replace('=', 'equals').replace('&', 'and').replace('\n', '. ').replace('*','')
        #
        args = {DatasetCreator.KEYS[i]:s for i,s in enumerate(line)}
        args['text'] = text
        if apply_filter: return apply_filter(args)
        return args
    @staticmethod
    def consider(create_line, s_args: Dict[str,Any], line: List[str]):
        if (args := DatasetCreator.filter(line, s_args['whitelist'], s_args['filter'])):
            fname,sample = args['fname'],s_args['sample']
            src,dst = s_args['wav_src']+fname, s_args['wav_dst']+fname
            if sample:
                y,sr = librosa.load(src, sr=sample, mono=True)
                soundfile.write(dst, y, sr)
            else:
                copy(src, dst) # very slow operation.
                pass
            return create_line(args)
    def run(self, outfile='./metadata.txt'):
        CORES,BS = 8,1<<6
        NAMES = ['wav_src', 'wav_dst', 'sample', 'whitelist']
        s_args = {k:self.__dict__[k] for k in NAMES}
        s_args['filter'] = self.apply_filter
        with open(self.csv_src) as csvfile: row_count = sum(1 for _ in csv.reader(csvfile))
        with open(self.csv_src) as csvfile, Pool(CORES) as pool, open(outfile, 'w') as json_file:
            reader = csv.reader(csvfile)
            next(reader) # ignore header
            for json_line in tqdm(pool.imap(partial(DatasetCreator.consider, self.create_line, s_args), reader, BS), total=row_count-1):
                if json_line: json_file.write(json_line+'\n') # this isn't pooled, but this is ok since consider() is much slower.
    def __init__(self,
                 create_line,
                 csv_src,
                 outfile='./MyNewDataset/metadata.txt',
                 wav_dst='./MyNewDataset/wavs/',
                 *,
                 apply_filter=None,
                 split=False,
                 whitelist: Optional[set]=None,
                 sample: Optional[int]=None,
                 wav_src='../0_original_data/AudioClip/',
                 ):
        if any(not os.path.exists(d) for d in [wav_src, csv_src]):
            raise FileNotFoundError
        for p in [outfile, wav_dst+'a']:
            d = Path(p).parent
            os.makedirs(d, exist_ok=True)
        self.wav_dst = wav_dst
        self.wav_src = wav_src
        self.csv_src = csv_src
        self.create_line = create_line
        self.sample = sample
        self.whitelist = whitelist
        self.apply_filter = apply_filter
        self.run(outfile)
        if split:
            filehead = outfile.split('.')
            extension = filehead.pop()
            filebase = '.'.join(filehead)
            split_file(outfile, filebase+'.train.'+extension, filebase+'.test.'+extension)

