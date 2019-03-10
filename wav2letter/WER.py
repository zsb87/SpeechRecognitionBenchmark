# Adapted from https://github.com/jpuigcerver/xer, thanks to jpuigcerver.
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
    for x in range(1, len(u) + 1):
        prev, curr = curr, [x] + ([None] * len(v))
        prev_ops, curr_ops = curr_ops, [(0, x, 0)] + ([None] * len(v))
        for y in range(1, len(v) + 1):
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
    fileRef = open('reference.txt')
    fileTranscription = open('transcription.txt')

    ref = fileRef.readlines()
    hyp = fileTranscription.readlines()

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
        textfile = open('result.txt', 'at')
        textfile.write('\nCER: %g%%, WER: %g%%, SER: %g%%' % (
                    (100.0 * (cer_s + cer_i + cer_d)) / cer_n,
                    (100.0 * (wer_s + wer_i + wer_d)) / wer_n,
                    (100.0 * sen_err) / len(ref)))
        textfile.close()