#!/usr/bin/python3
import os
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# this is for df.append()
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


### filepaths
os.chdir('../0_original_data')
JSON_DIALOG = './dialog.json'
JSON_VOCLIPS = './VoiceOverClipsLibrary.json'
WAV_AUDIOCLIPS_FOLDER = Path('./AudioClip')


### List /AudioClip/ folder
audio_assets = {wav_file.stem:wav_file for wav_file in WAV_AUDIOCLIPS_FOLDER.iterdir()}
print('loaded audio clips folder')


### Load VoiceOverClipsLibrary into clips{}
clips = {}
def aasset(k):
    v = audio_assets.get(k,None)
    if v is None: print(f"WARNING: Missing '{k}'")
def parseVoiceOver(vo):
    ID,AN,PATH = vo['ArticyID'], vo['AssetName'], vo['PathToClipInProject']
    expected_fname = PATH.split('\\').pop()
    if expected_fname[:-4] != AN: # INACCURATE AN DETECTED
        AN = expected_fname[:-4]
        assert AN[:6] == 'fixed-' # this is a very specific kind of file.
    path = audio_assets.get(AN,None)
    if path is None: return print(f"WARNING: Unable to find .wav file for: '{AN}'")

    clips[ID] = [path]
    for alt in sorted(vo['alternativeVoiceClips'], key=lambda alt: alt['AlternativeID']):
        #assert alt['AlternativeClipPath'].split('\\').pop()[:-4] == alt['AlternativeAssetName']
        # Alt assets do not appear to have the "fixed-" problem.
        clips[ID].append(audio_assets[alt['AlternativeAssetName']])

with open(JSON_VOCLIPS) as f:
    loaded = json.load(f)
    df_vo = pd.json_normalize(loaded, record_path=['clipInformations'])
    filtered = df_vo.filter(['AssetName','ArticyID','alternativeVoiceClips','PathToClipInProject'])
    filtered.apply(parseVoiceOver,axis=1)
print('parsed VoiceOverClipsLibrary')


### Load dialog.json into DataFrames
def iterate(values):
    return pd.Series({x["title"]: x["value"] for x in values})

with open(JSON_DIALOG) as f:
    loaded = json.load(f)
    df_actors_init = pd.json_normalize(loaded,record_path=['actors'])
    df_actors = pd.concat([df_actors_init, df_actors_init.pop('fields').apply(iterate)], axis=1)
    df_convos_init = pd.json_normalize(loaded,record_path=['conversations','dialogueEntries'])
    df_convos = pd.concat([df_convos_init, df_convos_init.pop('fields').apply(iterate)], axis=1)
print('Read huge dialog json file')


### Create processed csv file
df_final = pd.DataFrame(columns=[
    'fname',
    'acticyID',
    'alternativeIdx',
    'text',
    'actorID',
    'actorName'
]) # shape of the output csv

for aID,clip_ls in tqdm(clips.items(),desc='Building final csv...'):
    dialogueEntries = df_convos[df_convos["Articy Id"] == aID]
    if dialogueEntries.shape[0] == 0:
        print(f'WARNING: unused audio clip(s) {clip_ls}')
        continue
    assert dialogueEntries.shape[0] == 1 # make sure there's only 1 entry
    dialogueEntry = dialogueEntries.iloc[0] # get the entry
    actor = df_actors[df_actors.id == int(dialogueEntry.Actor)].iloc[0]
    for i,path in enumerate(clip_ls):
        text = dialogueEntry['Alternate%d'%i] if i else dialogueEntry['Dialogue Text']
        df_final = df_final.append({
            'fname': path.name,
            'acticyID': aID,
            'alternativeIdx': i,
            'text': text,
            'actorID': actor.id,
            'actorName': actor.Name,
        }, ignore_index=True)

df_final.to_csv(r'../1_initial_preproc/AudioClipMetadata.csv', index=False)
