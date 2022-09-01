import pandas as pd
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from termcolor import cprint
from json import load,dump,dumps

with open('./actors.json') as f: actors = load(f)['actors']
df = pd.read_csv('./AudioClipMetadata.csv')

res = []
def handle(opt: str):
    print()
    if not opt: print(dumps(res))
    elif opt == 'back': res.pop()
    elif len(actors) > len(res): res.append({**actors[len(res)], 'narratorType': opt})
    else: print('press q bro')
    #
    while 1:
        if len(actors) == len(res): break
        a = actors[len(res)]
        cprint(a['name'], 'magenta', None, ['bold', 'underline'])
        desc = a.get('longDescription','')
        if desc: cprint(desc, 'yellow')
        else: cprint('No description', 'grey')
        #
        lines = df[df['actorID'] == a['actorId']]
        if lines.shape[0]:
            print(lines)
            break
        else:
            cprint('No lines found for this Actor. Skipping...', 'grey')
            res.append({**actors[len(res)], 'narratorType': 'Absent'})
    print('> ', end='')

bindings = KeyBindings()

def bind(c: str, out: str):
    @bindings.add(c)
    def _(e): handle(out)
bind('enter', '')
bind('b', 'back')
bind('1', 'NPC')
bind('2', 'Narrator')
bind('3', 'Unknown')
bind('4', 'Mixed')

@bindings.add('q')
def finish(e):
    with open('actors_by_narrator.json', 'w') as f: dump(res,f)
    exit()

prompt("Press enter to begin: ", key_bindings=bindings)


