# Speech Recognition Benchmark

A comprehensive evaluation of currently existing Automatic Speech Recognition (ASR) systems.



## Noisy Audio Synthesis
We made a Python code that can duplicate audio dataset's folder tree structure and add noise onto audio files. 

Python packages we used for noisy audio synthesis code are: `docopt`, `pydub`, `numpy`, `os`, `fnmatch`, `shutil`.

Please make sure install all of them before running the code. You can install them by running following line:
```
pip install docopt pydub numpy os fnmatch shutil
```

The usage of the noisy audio synthesis code on commnad-line is:
```
python make_noisy_dataset.py <audio_dataset_dir> <noise_dataset_dir> <destination_dir> <file_type> <snr>
```
For example, `python make_noisy_dataset.py 'LibriSpeech/' '15 Free Ambient Sound Effects/Busy City Street.mp3' './' 'wav' 0`. Also, please don't forget to include `'/'` at the end of `<audio_dataset_dir>` or `<destination_dir>`.

You can adjust how much noise corrupted the audio file by adjusting SNR value in decibel scale. SNR means signal-to-noise ratio, and it is simply how much the audio is corrupted by the noise. 

We used some free open source noise files, which were downloaded [here](http://pbblogassets.s3.amazonaws.com/uploads/2016/09/15-Free-Ambient-Sound-Effects.zip). However, you can use any other noise files other than these.


## DeepSpeech Model
Architecture from paper [Baidu's Deep Speech Paper](https://arxiv.org/abs/1412.5567). Framework implemented by Mozilla. We made the WER result implementation part.

### Steps:
1. Download .so file from [here](https://drive.google.com/file/d/1c2o3P9OY87S6vCpJO2KCKRQQAhOO_gHb/view?usp=sharing).
2. Run `DeepSpeech-mozilla/batch_trans_xer.py`to generate transcripts from audio input and save in .txt files and then calculate the WER, CER and SER results from generated transcritps and labels.


## Wav2Letter Model
1. Run `result.py` to calculate the WER results from generated transcritps and labels.



## WaveNet Model

### Requirement
(Correction appended to original [owner's repository](https://github.com/buriburisuri/speech-to-text-wavenet))

libsndfile: check installation on [libsndfile](https://github.com/erikd/libsndfile) (`brew install libsndfile` for Mac)