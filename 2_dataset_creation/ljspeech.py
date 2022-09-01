from typing import Dict
from dataset_creator import DatasetCreator
def create_line(args: Dict[str,str]):
    return f'{args["wav_dst"]}|{args["text"]}'

DatasetCreator(create_line, outfile='./LJSpeech_txt/AudioClips_Narrator.ljs.txt', wav_dst='./LJSpeech_txt/wavs/out/', split=True)

