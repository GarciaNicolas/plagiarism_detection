import spacy
import pandas as pd
import numpy as np
import re 


df = pd.read_csv('./data.csv')
nlp = spacy.load('es_core_news_lg')
author_synonyms = ['nombre','nombres','apellido','apellidos','nombre y apellido','apellido y nombre','nombres y apellidos','apellidos y nombres','alumno','alumnos', 'alumna','alumne','alumnes']

def merge_dataframes(df1, df2):
    return pd.concat([df1,df2], ignore_index=True)

def append_to_dictionary(dic, key, element):
    dic.setdefault(key, {'n_sentence': 0, 'plagiarism': []})
    dic[key]['plagiarism'] += element
    