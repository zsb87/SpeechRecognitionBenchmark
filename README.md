# Speech Recognition Benchmark

A comprehensive evaluation under different types and levels of environment noises using two currently existing Automatic Speech Recognition (ASR) systems.


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
This is a wrapper of [DeepSpeech-Mozilla](https://github.com/mozilla/DeepSpeech). Architecture is from paper [Baidu's Deep Speech Paper](https://arxiv.org/abs/1412.5567). Framework is implemented by Mozilla. We use its speech recognition inference module and implemented the WER result part.

Decoder: CTC + language model beam search

Language model: KenLM

### Steps:
1. Download .so file from [here](https://drive.google.com/file/d/1c2o3P9OY87S6vCpJO2KCKRQQAhOO_gHb/view?usp=sharing).
2. Install DeepSpeech with `pip3 install deepspeech`.
3. Run `DeepSpeech-mozilla/batch_trans_xer.py`to generate transcripts from audio input and save in .txt files and then calculate the WER, CER and SER results from generated transcritps and labels.


## wav2letter Model
This is a wrapper of [wav2letter++](https://github.com/facebookresearch/wav2letter) model by Facebook AI Research. wav2letter++ is a fast open source speech processing toolkit from the Speech Team at Facebook AI Research. It is written entirely in C++ and uses the ArrayFire tensor library. Because there is some error in the pretrained model, we slightly modified the codes and trained it on the librispeech’s train-clean-100 dataset for 24 hours. Also we made the WER result implementation part.

Decoder: CTC + language model beam search

Language model: [3-gram LM](http://www.openslr.org/resources/11/3-gram.arpa.gz) trained from libriSpeech corpus

### Steps:
1. Install wav2letter with docker using `sudo docker run --runtime=nvidia --rm -itd --ipc=host --name w2l wav2letter/wav2letter:cuda-latest`.
2. Run `Split.py` to extract and save the labels in correct format.
3. Run `WER` to calculate the WER results from generated transcritps and labels.

