from typing import Dict
from dataset_creator_nonnarrator import DatasetCreator
def create_line(args: Dict[str,str]):
    return f'wavs/{args["fname"]}|{args["text"]}'
def reject(args: Dict[str,str]):
    if 'COALITION WARSHIP ARCHER' in args['fname']: return
    return args

DatasetCreator(create_line, csv_src="../1_initial_preproc/kk.csv",
               outfile='./TalkNetDataset_kk/metadata.txt', wav_dst='./TalkNetDataset_kk/wavs/',
               apply_filter=reject, split=True)

