# Adapted from https://github.com/jpuigcerver/xer, thanks to jpuigcerver.
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse

logging.basicConfig(
    format='%(levelname)s(%(filename)s:%(lineno)d): %(message)s')

def list_files_in_directory(mypath):
    return [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

def levenshtein(u, v):
    prev = None
    curr = [0] + range(1, len(v) + 1)
    # Operations: (SUB, DEL, INS)
    prev_ops = None
    curr_ops = [(0, 0, i) for i in range(len(v) + 1)]
    for x in xrange(1, len(u) + 1):
        prev, curr = curr, [x] + ([None] * len(v))
        prev_ops, curr_ops = curr_ops, [(0, x, 0)] + ([None] * len(v))
        for y in xrange(1, len(v) + 1):
            delcost = prev[y] + 1
            addcost = curr[y - 1] + 1
            subcost = prev[y - 1] + int(u[x - 1] != v[y - 1])
            curr[y] = min(subcost, delcost, addcost)
            if curr[y] == subcost:
                (n_s, n_d, n_i) = prev_ops[y - 1]
                curr_ops[y] = (n_s + int(u[x - 1] != v[y - 1]), n_d, n_i)
            elif curr[y] == delcost:
                (n_s, n_d, n_i) = prev_ops[y]
                curr_ops[y] = (n_s, n_d + 1, n_i)
            else:
                (n_s, n_d, n_i) = curr_ops[y - 1]
                curr_ops[y] = (n_s, n_d, n_i + 1)
    return curr[len(v)], curr_ops[len(v)]

# def levenshtein(a,b):
#     "Calculates the Levenshtein distance between a and b."
#     n, m = len(a), len(b)
#     if n > m:
#         # Make sure n <= m, to use O(min(n,m)) space
#         a,b = b,a
#         n,m = m,n
#     current = list(range(n+1))
#     for i in range(1,m+1):
#         previous, current = current, [i]+[0]*n
#         for j in range(1,n+1):
#             add, delete = previous[j]+1, current[j-1]+1
#             change = previous[j-1]
#             if a[j-1] != b[i-1]:
#                 change = change + 1
#             current[j] = min(add, delete, change)
#     return current[n]

def load_file(fname, encoding):
    try:
        f = open(fname, 'r')
        data = []
        for line in f:
            data.append(line.rstrip('\n').rstrip('\r').decode(encoding))
        f.close()
    except:
        logging.error('Error reading file "%s"', fname)
        exit(1)
    return data

def load_file_batch(fnames, encoding):
    try:
        data = []
        for fname in fnames:
            if not fname.endswith('.DS_S.txt') and not fname.endswith('.DS_Store'):
                f = open(fname, 'r')
                for line in f:
                    data.append(line.upper())
                    # data.append(line.rstrip('\n').rstrip('\r').decode(encoding))
                f.close()
    except:
        logging.error('Error reading file "%s"', fname)
        exit(1)
    return data

if __name__ == '__main__':
    input_source = 'files'
    # input_source = 'str'
    separator = '\t'
    encoding = 'utf-8'

    process_history = {
        'Edinburgh_noisy': {
            'reference_folder': '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/Edinburgh/testset_txt/',
            'transcription_folder': '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/Edinburgh/clean_transcripts/',
        }
    }

    transcription_folder = '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/LibriSpeech_dataset/clean_transcripts'
    reference_folder = '/Users/shibozhang/Documents/Course/DeepLearningTopics_496/dataset/LibriSpeech_dataset/test_clean/txt/'

    references = [os.path.join(reference_folder, i) for i in list_files_in_directory(transcription_folder)]
    transcriptions = [os.path.join(transcription_folder, i[:-4]+'.txt') for i in list_files_in_directory(transcription_folder)]

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
