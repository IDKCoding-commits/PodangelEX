This project leverage's OpenAI's Whisper model, allowing you to input a list of audio files and cut out not only specifc swear words, but also any swears based in
context. This project cannot promise 100% accuracy, however, the accuracy is at the very least that of 80%, though this number is just an estimate*.

This project is a revitalization of a passion project that got me into Python. Compared to the first verion, PodAngelEX supports:

    Multiple workers, vastly decreasing time needed to clean large lists of files at the expense of VRAM

    Simple config for context thresholds, paths, model size, etc

    Cuts rather than mutes to avoid long periods of silence

To get started, just:
    1. run pip install -r utils.txt
    2. run main.py
    3. Complete config init
Then you can put your audio files into the Input folder that should get created, and run the transcription.

Side note: I do realize there are a few warnings that show up, at least on Mac. As far as I know, these warnings don't refrence anything important, and are more annoying than anything else. If there is a real issue that I failed to notice, please let me know! 


*These numbers are based off of fine-tuned thresholds according to my personal standards, and the Turbo model size