# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 10:15:02 2023

@author: Pierre
"""
import os

repertoire = "C:/Users/Pierre/Videos/"
liste = os.listdir(repertoire)
for n_fichier in liste:
    if "SNK" in n_fichier:
        nom = n_fichier
        nom = nom.replace("264","265").replace("Aac","Opus Stereo")
        # nom = nom.replace("{","[").replace("}","]")
        print(nom)
        os.rename(repertoire + n_fichier, repertoire + nom)
