# potentially broken have not tested
import wave
import contextlib
from shutil import copy
from typing import Dict
from json import dumps,load
from dataset_creator import DatasetCreator


# https://stackoverflow.com/a/7833963
# 2.2565208333333335 == duration('./AudioClip/ANTI OBJECT TASK FORCE_TITLE.wav'))
def duration(fname: str) -> float:
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

def create_line(args: Dict[str,str]):
    fname,wav_src,wav_dst = args['fname'], args['wav_src'], args['wav_dst']
    t = duration(wav_src+fname)
    return dumps({'audio_filepath': wav_dst+fname, 'text': args['text'], 'duration': t})

DatasetCreator(create_line, outfile='./NeMo_json/AudioClips_Narrator.json', wav_dst='./NeMo_json/AudioClip_Narrator/')



