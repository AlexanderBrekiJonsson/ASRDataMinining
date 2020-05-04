import numpy as np
import wave
import struct
import math
import matplotlib.pyplot as plt
import librosa as lr
import nltk

def where_silent(audio, frq, amp_thres=0.002, time_thres=0.2):
    silent = []

    for i in range(0,len(audio)):
        if audio[i]<amp_thres: silent.append(1)
        else: silent.append(0)

    min_length = frq*time_thres
    counter = 0
    for i in range(0,len(audio)):
        if silent[i]==0:
            if counter <= min_length:
                for j in range(i-counter, i):
                    silent[j]=0
            counter = 0
        elif silent[i]==1:
            counter = counter+1
    counter = 0
    for i in range(0,len(audio)):
        if silent[i]==1:
            if counter <= min_length:
                for j in range(i-counter, i):
                    silent[j]=1
            counter = 0
        elif silent[i]==0:
            counter = counter+1
    return silent
def smooth(audio,frq):
    org_length = len(audio)
    i=1
    out_audio = []
    if org_length%2 == 0:
        while i < org_length:
            out_audio.append((audio[i-1]+audio[i])/2)
            i = i + 2
    else:
        while i < org_length:
            out_audio.append((audio[i-1]+audio[i])/2)
            i = i + 2
        out_audio.append(audio[org_length-1])

    out_frq = frq/2
    return np.array(out_audio), out_frq
def smooth_to(audio,frq,to_frq):
    smooth_audio = audio
    smooth_frq = frq
    while smooth_frq > to_frq:
        smooth_audio, smooth_frq = smooth(smooth_audio,smooth_frq)
        print(smooth_frq)
    return smooth_audio, smooth_frq
def silent_list(silent, frq):
    section = []
    prev_silent = True
    for i in range(0,len(silent)):
        if silent[i]==0 and prev_silent == True:
            start = i
            prev_silent = False
        elif silent[i]==1 and prev_silent == False:
            section.append((start/frq,i/frq))
            prev_silent = True
        elif i == len(silent)-1:
            section.append((start/frq,i/frq))
    return section
def segment(w_silent, w_silent_frq, audio, frq):
    segments = []
    length_s = len(w_silent)
    length_a = len(audio)

    i=0
    start_index=0
    while i < length_s:
        if w_silent[i]==1:
            j = i
            while j<length_s and w_silent[j]==1:
                j=j+1
            end_index = math.ceil(((i+j)/2)*(frq/w_silent_frq))
            segments.append(audio[start_index:end_index])
            start_index = end_index
            i=j
        i=i+1

    return segments
def split_indexes(w_silent, w_silent_frq, audio, frq):
    segment_ends = []
    length_s = len(w_silent)
    length_a = len(audio)
    i=0
    start_index=0
    while i < length_s:
        if w_silent[i]==1:
            j = i
            while j<length_s and w_silent[j]==1:
                j=j+1
            end_index = math.ceil(((i+j)/2)*(frq/w_silent_frq))
            segment_ends.append(end_index)

            i=j
        i=i+1
    segment_ends[len(segment_ends)-1] = len(audio)-1
    return segment_ends
def relative_cumulative_size(list):
    total_length = 0
    for i in list:
        total_length = total_length + len(i)

    relative_lengths = []
    running = 0
    for i in list:
        running = running+len(i)/total_length
        relative_lengths.append(running)
    return relative_lengths

def closest_index(value, list):
    diff = 10
    index=-1
    for i in range(0, len(list)):
        if abs(value-list[i])<diff:
            diff = abs(value-list[i])
            index = i
    return index

def split_by_paragraph(wav_path, txt_path):
    txtfile= open(txt_path,'r')
    txt = txtfile.read()
    txtfile.close()

    paragraphs = txt.split('\n\n')
    for i in paragraphs: i = i.replace('\n', ' ')

    number_of_paragraphs = len(paragraphs)
    paragraph_crl = relative_cumulative_size(paragraphs)

    audio, frq = lr.load(wav_path)
    smooth_audio, smooth_frq = smooth_to(abs(audio),frq,500)

    number_of_splits = 0
    silence_length = 1
    while number_of_splits <= 4*number_of_paragraphs:
        silence_length = silence_length*0.9
        w_silent = where_silent(smooth_audio, smooth_frq, 0.002, silence_length)
        index_of_splits = split_indexes(w_silent,smooth_frq,audio,frq)
        number_of_splits = len(index_of_splits)

    audio_crl = np.array(index_of_splits)/len(audio)

    # match
    paragraph_splits = []
    for i in range(0,len(paragraph_crl)):
        paragraph_splits.append(closest_index(paragraph_crl[i],audio_crl))

    for i in range(0,number_of_paragraphs):
        print('index: ' + str(i))
        print('paragraph_split: ' + str(paragraph_splits[i]))
        print(paragraphs[i])
        print('-----------------------')

    segments = []
    j=0
    for i in paragraph_splits:
        segments.append(audio[j:index_of_splits[i]])
        j=index_of_splits[i]


    x=1
    for i in segments:
        string = 'segment_' + str(x) + '.wav'
        lr.output.write_wav(string, i, frq)
        x=x+1
    print(paragraph_crl)



def split_by_sentence(text_list, audio_list):
    pass

if __name__== "__main__":
    split_by_paragraph('Chapter3.wav', 'Chapter3.txt')
