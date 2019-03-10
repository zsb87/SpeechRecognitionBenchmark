#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: minyoungpark

usage: make_noisy_dataset.py <audio_dataset_dir> <noise_dataset_dir> <destination_dir> <file_type> <snr>

"""

from docopt import docopt
from pydub import AudioSegment
import numpy as np
import os, fnmatch, shutil


# Create a noisy audio dataset, which has the same folder tree with the original dataset, with given SNR value
# Also copy transcript files to the same location as the original dataset to the noisy dataset
def make_noisy_dataset(audio_dataset_dir, noise_dataset_dir, destination_dir
                       , file_type, snr):   
    
    # Create empty folders mimicing the folder tree of audio dataset
    try: 
        current_dir = os.getcwd()
        print('Creating a folder to put a noisy dataset.')
        audio_dataset_folder = os.path.basename(os.path.dirname(audio_dataset_dir))
        audio_filename = os.path.basename(noise_dataset_dir)
        output_dir = destination_dir + '/' + audio_filename[:-4] + '/snr' + str(snr) + '/' + audio_dataset_folder + '/'   
        shutil.copytree(audio_dataset_dir, output_dir, ignore=_ig_f)
        
    except FileExistsError:
        print('Folder already exists.')
        
    finally:
        print('Creating noisy audio files....')
        noise = AudioSegment.from_file(noise_dataset_dir)
        os.chdir(os.path.dirname(os.path.abspath(audio_dataset_dir)))
        _make_noisy_audio(audio_dataset_folder, audio_filename, destination_dir, file_type, noise, snr)
        _copy_transcript(audio_dataset_folder, audio_filename, destination_dir, '*.txt')
        _copy_transcript(audio_dataset_folder, audio_filename, destination_dir, '*.TXT')
        os.chdir(current_dir)
    

# Helper function to copy empty folders of audio dataset into destination
def _ig_f(dir, files):
    
    return [f for f in files if os.path.isfile(os.path.join(dir, f))]

# Copy transcript file to the same location as the original dataset to the noisy dataset
def _copy_transcript(audio_dataset_folder, audio_filename, destination, file_type):
    
    # Search for files inside the folder
    for entry in os.listdir(audio_dataset_folder):
        
        # Check if the files have "file_type"
        if fnmatch.fnmatch(entry, file_type):
            # Copy the transcript file
            shutil.copy(audio_dataset_folder + '/' + entry, destination + audio_filename[:-4] + '/snr' + str(snr) + '/' + audio_dataset_folder + '/' + entry)
            
        elif os.path.isdir(audio_dataset_folder + '/' + entry):
            # Recursively search for a transcript file and copy it
            _copy_transcript(audio_dataset_folder + '/' + entry, audio_filename, destination_dir, file_type)


# Recursively search audio files with file_type argument, and then copy the audio with noise added into the destination
def _make_noisy_audio(audio_dataset_folder, audio_filename, destination, file_type, noise, snr):
    
    # Search for files inside the folder
    for entry in os.listdir(audio_dataset_folder):
        
        # Check if the files have "file_type"
        if fnmatch.fnmatch(entry, file_type):
            print('Adding noise to ' + entry)
            sound = AudioSegment.from_file(audio_dataset_folder + '/' + entry)
            snr_in_dB = 20*np.log10(sound.rms / noise.rms)
            # Pick a random interval of the noise because the noise is longer
            noise_start_time = np.random.rand()*(noise.duration_seconds - sound.duration_seconds)
            # Combine audio and noise with specified SNR value
            combined = sound.overlay(noise[1e3*noise_start_time:], gain_during_overlay=-snr_in_dB + float(snr))
            # Create a noisy audio
            combined.export(destination + audio_filename[:-4] + '/snr' + str(snr) + '/' + audio_dataset_folder + '/' + entry, format = file_type[2:])
            
        elif os.path.isdir(audio_dataset_folder + '/' + entry):
            # Recursively search for an audio and create a noisy audio
            _make_noisy_audio(audio_dataset_folder + '/' + entry, audio_filename, destination_dir, file_type, noise, snr)


if __name__ == "__main__":
    
    args = docopt(__doc__)
    audio_dataset_dir = args["<audio_dataset_dir>"]
    noise_dataset_dir = args["<noise_dataset_dir>"]
    destination_dir = args["<destination_dir>"]
    file_type = args["<file_type>"]
    file_type = '*.' + file_type
    snr = args["<snr>"]
    
    make_noisy_dataset(audio_dataset_dir, noise_dataset_dir, destination_dir, file_type, snr)
