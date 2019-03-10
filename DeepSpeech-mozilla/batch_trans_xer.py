#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os
import argparse
import numpy as np
import shlex
import subprocess
import sys
import wave
from deepspeech import Model, printVersions
from timeit import default_timer as timer
import random
import logging
from utils import list_files_in_directory, levenshtein, load_file, load_file_batch, convert_samplerate

try:
    from shhlex import quote
except ImportError:
    from pipes import quote


def _intersection(a, b):
    return list(set(a) & set(b))

def _pickup_continue():   
    audios = list_files_in_directory(audiofolder)
    files_done = list_files_in_directory(transcription_folder)
    audios = [i[:-4] for i in audios]
    files_done = [i[:-4] for i in files_done]

    files_left = list(set(audios) - set(files_done))
    files_left = [i+'.wav' for i in files_left]
    audio_list = [os.path.join(audiofolder, i) for i in files_left]



# These constants control the beam search decoder
# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 100
# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_ALPHA = 0.75
# The beta hyperparameter of the CTC decoder. Word insertion bonus.
LM_BETA = 1.85


# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26
# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9


def main():

    model = '../models/output_graph.pbmm'
    alphabet = '../models/alphabet.txt'
    lm = '../models/lm.binary'
    trie = '../models/trie'

    samples = 200 
    
    # '/Volumes/Seagate/Dataset/Coffee Shop/snr0/LibriSpeech/test_clean/wav'
    snr = 20

    audiofolder = '/Volumes/Seagate/Dataset/Coffee Shop/snr'+str(snr)+'/librispeech_orig_cropped/test_clean/wav'
    transcription_folder = '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/Coffee Shop/snr'+str(snr)+'/LibriSpeech/test_clean/transcripts/'
    
    reference_folder = '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/LibriSpeech_dataset/raw/test_clean/txt/'
    result_file = '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/results.txt'


    if not os.path.exists(transcription_folder):
        os.makedirs(transcription_folder)
    
    audio_files = list_files_in_directory(audiofolder)
    print('number of audio clips: ', str(len(audio_files)))
    random.shuffle(audio_files)
    audio_files = audio_files[0:samples]

    audio_list = [os.path.join(audiofolder, i) for i in audio_files]
    savefiles = [os.path.join(transcription_folder, i[:-4]+'.txt') for i in audio_files]


    print('Loading model from file {}'.format(model), file=sys.stderr)
    model_load_start = timer()
    ds = Model(model, N_FEATURES, N_CONTEXT, alphabet, BEAM_WIDTH)
    model_load_end = timer() - model_load_start
    print('Loaded model in {:.3}s.'.format(model_load_end), file=sys.stderr)

    if lm and trie:
        print('Loading language model from files {} {}'.format(lm, trie), file=sys.stderr)
        lm_load_start = timer()
        ds.enableDecoderWithLM(alphabet, lm, trie, LM_ALPHA, LM_BETA)
        lm_load_end = timer() - lm_load_start
        print('Loaded language model in {:.3}s.'.format(lm_load_end), file=sys.stderr)

    for audio, savefile in zip(audio_list, savefiles):
        fin = wave.open(audio, 'rb')
        fs = fin.getframerate()
        if fs != 16000:
            print('Warning: original sample rate ({}) is different than 16kHz. Resampling might produce erratic speech recognition.'.format(fs), file=sys.stderr)
            fs, audio = convert_samplerate(audio)
        else:
            audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        audio_length = fin.getnframes() * (1/16000)
        fin.close()
        print('Running inference.', file=sys.stderr)
        inference_start = timer()
        transcription = ds.stt(audio, fs)
        print(transcription)
        textfile = open(savefile, 'w')
        textfile.write(transcription)
        textfile.close()

        inference_end = timer() - inference_start
        print('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, audio_length), file=sys.stderr)
        input_source = 'files'



    # input_source = 'str'
    separator = '\t'
    encoding = 'utf-8'

    references = [os.path.join(reference_folder, i) for i in list_files_in_directory(transcription_folder)]
    transcriptions = [os.path.join(transcription_folder, i[:-4]+'.txt') for i in list_files_in_directory(transcription_folder)]

    print(len(references))
    print(len(transcriptions))
    # exit()
    # references, transcriptions = _intersection(references, transcriptions)

    ref, hyp = [], []

    if input_source == 'str':
        ref.append(reference.decode(encoding))
        hyp.append(transcription.decode(encoding))
    elif input_source == '-':
        line_n = 0
        for line in sys.stdin:
            line_n += 1
            line = line.rstrip('\n').rstrip('\r').decode(encoding)
            fields = line.split(separator)
            if len(fields) != 2:
                logging.warning(
                    'Line %d has %d fields but 2 were expected',
                    line_n, len(fields))
                continue
            ref.append(fields[0])
            hyp.append(fields[1])
    elif input_source == 'file':
        ref = load_file(reference, encoding)
        hyp = load_file(transcription, encoding)
        if len(ref) != len(hyp):
            logging.error(
                'The number of reference and transcription sentences does not '
                'match (%d vs. %d)', len(ref), len(hyp))
            exit(1)
    elif input_source == 'files':
        ref = load_file_batch(references, encoding)
        hyp = load_file_batch(transcriptions, encoding)
        if len(ref) != len(hyp):
            logging.error(
                'The number of reference and transcription sentences does not '
                'match (%d vs. %d)', len(ref), len(hyp))
            exit(1)
    else:
        logging.error('INPUT FROM "%s" NOT IMPLEMENTED', input_source)
        exit(1)

    wer_s, wer_i, wer_d, wer_n = 0, 0, 0, 0
    cer_s, cer_i, cer_d, cer_n = 0, 0, 0, 0
    sen_err = 0
    for n in range(len(ref)):
        if n%100 == 0:
            print('processing {}'.format(n))
        # update CER statistics
        _, (s, i, d) = levenshtein(ref[n], hyp[n])
        cer_s += s
        cer_i += i
        cer_d += d
        cer_n += len(ref[n])
        # update WER statistics
        _, (s, i, d) = levenshtein(ref[n].split(), hyp[n].split())
        wer_s += s
        wer_i += i
        wer_d += d
        wer_n += len(ref[n].split())
        # update SER statistics
        if s + i + d > 0:
            sen_err += 1

    if cer_n > 0:
        print ('CER: %g%%, WER: %g%%, SER: %g%%' % (
                    (100.0 * (cer_s + cer_i + cer_d)) / cer_n,
                    (100.0 * (wer_s + wer_i + wer_d)) / wer_n,
                    (100.0 * sen_err) / len(ref)))
        # save results
        textfile = open(result_file, 'a')
        textfile.write('\n\n'+transcription_folder)
        textfile.write('\nCER: %g%%, WER: %g%%, SER: %g%%' % (
                    (100.0 * (cer_s + cer_i + cer_d)) / cer_n,
                    (100.0 * (wer_s + wer_i + wer_d)) / wer_n,
                    (100.0 * sen_err) / len(ref)))
        textfile.close()

if __name__ == '__main__':
    main()
