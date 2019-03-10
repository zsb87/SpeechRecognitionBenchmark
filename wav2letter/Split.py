f = open("libri-clean-city-snr20.txt")
fileRef = open('reference.txt', 'wt')
fileTranscription = open('transcription.txt', 'wt')
lines = f.readlines()

i = 0

while i < len(lines):
    rline = lines[i]
    tline = lines[i+1]
    fileRef.write(rline[5:])
    fileTranscription.write(tline[5:])
    i += 3

fileTranscription.close()
fileRef.close()
f.close()
