# Speech Recognition Benchmark

A comprehensive evaluation of currently existing Automatic Speech Recognition (ASR) systems.



## Noisy Audio Synthesis
Python packages we used for noisy audio synthesis code are: `docopt`, `pydub`, `numpy`, `os`, `fnmatch`, `shutil`.

Please make sure install all of them before running the code. 


## DeepSpeech Model
Architecture from paper [Baidu's Deep Speech Paper](https://arxiv.org/abs/1412.5567). Framework implemented by Mozilla. We made the WER result implementation part.

### Steps:
0. Download .so file from [here](https://drive.google.com/file/d/1c2o3P9OY87S6vCpJO2KCKRQQAhOO_gHb/view?usp=sharing).
1. Run `DeepSpeech-mozilla/batch_transcript.py`to generate transcripts from audio input and save in  txt files.
2. Run `DeepSpeech-mozilla/result.py`to calculate the WER and CER results from generated transcritps and labels.


## Wav2Letter Model



## WaveNet Model
