# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 00:06:18 2023

@author: Pierre
"""
#########Adapt to your needs#########
#########Take care of spaces in the commands#########
#########Make sure you have ffmpeg and mkvmerge#########


import subprocess
import json
import os
from pymkv.MKVFile import MKVFile
import time

t0 = time.time()
ecraser = "-y" #overwrite
copie_video = True #copy video stream
copie_sous_titres = True #copy subtitles streams
#Let quotations mark to ensure cmd reads the spaces
#example
dossier_source = "C://Users//Pierre//Videos//" #source directory
dossier_cible = "C://Users//Pierre//Videos//" #target directory
vids = []
for filename in os.listdir(dossier_source):
    f = os.path.join(dossier_source, filename)
    if os.path.isfile(f) and (f[-3:]=="mkv" or f[-3:]=='mp4'): #only take .mkv and .mp4 files
        vids.append(filename)
for video in vids:
    t1 = time.time()
    print("Début " + video)
    ######Infos#########
    #ffprobe shows informations about the file
    source = '"' + dossier_source + "//" + video + '"' + " "
    commande2 = 'ffprobe -v quiet -print_format json -show_format -show_streams -print_format json ' + source[:-1]
    resultat = subprocess.run(commande2, shell=True, stdout=subprocess.PIPE)
    resultat = json.loads(resultat.stdout)
    streams = []
    for stream in resultat['streams']:
        codec_type = stream['codec_type']
        streams.append([codec_type])
        if codec_type == 'audio' or codec_type == 'subtitle':
            streams[-1].append(stream['tags']['language'])
            if 'title' in stream['tags']:
                streams[-1].append(stream['tags']['title'])
            else:
                streams[-1].append(0)
        if codec_type == 'audio':
            streams[-1].append(stream['channel_layout'])
    
    a_br = 128 #audio bitrate in kbps, Opus at 128 kbps in stereo is rather grat, don't see any difference with original
    format_audio = '-af "channelmap=channel_layout=5.1(side)" ' #https://trac.ffmpeg.org/ticket/5718
    cible = '"' + dossier_cible + "//" + video + '"' + " "
    ######Encodage#########
    #could adapt of cases where more than 2 audio streams are contained
    channel1 = streams[1][3] #streams[1] and streams[2] are audio streams most of the time, could be adapted easily given the fact that streams contain the stream type
    channel2 = streams[2][3]
    #commande = "ffmpeg " + "-i " + source + "-map 0 " + copie_video*"-c:v copy "+ copie_sous_titres*"-c:s copy " + "-c:a " + "libopus " + "-b:a " + str(a_br)+"K " + format_audio + "-ac 2 " + cible + ecraser
    commande = "ffmpeg " + "-i " + source + "-map 0 " + copie_video*"-c:v copy "+ copie_sous_titres*"-c:s copy " + "-c:a " + "libopus " + "-b:a " + str(a_br)+"K " + '-filter:a:1 "channelmap=channel_layout=' + channel2 + '" ' + '-filter:a:0 "channelmap=channel_layout=' + channel1 + '" ' + "-ac 2 " + cible + ecraser
    subprocess.run(commande,shell=True)
    cible = cible[1:-2]
    mkv_file = MKVFile(cible)
    #######Version 1 : subtitles are well labelized with right language
    #######choix forced et full
    #check if there is only one french subtitle stream (only forced) or two (forced and full)
    #warning: doesn't handle other cases
    #mediainfo should do the trick by analysing the size of each stream (forced<<full)
    n_fr = 0
    for track in mkv_file.tracks:
        print(track.track_name)
        if track.track_type=="subtitles" and track.language=='fre':
            n_fr+=1
    if n_fr==1:
        a = 1
    if n_fr==2:
        a=0
    # a = 0
    # a = 1
    for track in mkv_file.tracks:
        if track.track_type == "video":
            track.language="zxx" #"no linguistic content" could also use the original language of the video
        if track.track_type=="audio":
            if track.language=="eng":
                track.track_name = "VO EN" #renames
                track.default_track = False
            else:
                track.track_name = "VFF" #rename
                track.default_track = True #sets default_track
        if track.track_type=="subtitles":
            if track.language=="eng":
                #track.track_name = "English Full"
                track.default_track = False
            if track.language=='fre':
                if a==0:
                    track.default_track = True
                    #track.track_name = "French Forced"
                    a+=1
                else:
                    track.default_track = False  
                    #track.track_name = "French Full"
    #Version 2 : subtitles are not well labelized (not right language) but right title
    # for track in mkv_file.tracks:
    #     if track.track_type == "video":
    #             track.language="zxx"
    #     if track.track_type=="audio":
    #         if track.language=="eng":
    #             track.track_name = "VO"
    #             track.default_track = False
    #         else:
    #             track.track_name = "VFF"
    #             track.default_track = True
    #     if track.track_type=="subtitles":
    #         if "VO" in track.track_name:
    #             track.language = "eng"
    #             track.track_name = "VO Full"
    #             track.default_track = False
    #         if "VFF" in track.track_name:
    #             track.language = "fre"
    #             if "Forced" in track.track_name:
    #                 track.default_track = True  
    #                 track.track_name = "VFF Forced"
    #             elif "Full" in track.track_name:
    #                 track.default_track = False  
    #                 track.track_name = "VFF Full"
    mkv_file.mux(cible[:-3] + "2.mkv",silent=True) #muxes in another file
    os.remove(cible) #remove the wrong labelized file
    os.renames(cible[:-3] + "2.mkv", cible) #rename the muxed file
    print("Fin " + video)
    print("Durée : " + str(time.time()-t1)) #shows encoding time
print("Durée totale : " + str(time.time()-t0)) #shows the total encoding time