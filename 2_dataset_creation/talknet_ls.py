from typing import Dict
from dataset_creator_nonnarrator import DatasetCreator
def create_line(args: Dict[str,str]):
    return f'wavs/{args["fname"]}|{args["text"]}'
def reject(args: Dict[str,str]):
    return args

DatasetCreator(create_line, csv_src="../1_initial_preproc/ls.csv",
               outfile='./TalkNetDataset_ls/metadata.txt', wav_dst='./TalkNetDataset_ls/wavs/',
               apply_filter=reject, split=True)

