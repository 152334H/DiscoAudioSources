# Data processing
`preproc.py` reads the data from the `0_*` folder to create `AudioClipsMetadata.csv`. It takes a while to run, because the code is very inefficient (I am inexperienced with `pandas`).

`check_for_multiuse_audio.py` checks for audio clips that are referenced by multiple dialogue lines. If it shows duplicates for lines of your voice actor, you have to fix that somehow.

`manual_labour.py` creates the `actors_by_narrator.json` file, via -- you guessed it -- manual labour.

`speaker_frequency.py` dumps the number of lines per speaker in ascending order.

