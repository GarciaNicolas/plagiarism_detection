from helper import *
from author import *
from topic import *

import spacy
import re

nlp = spacy.load('es_core_news_lg')

messy_author_strings = ['nombre','nombres','apellido','apellidos','nombre y apellido','apellido y nombre','nombres y apellidos','apellidos y nombres','alumno','alumnos', 'alumna','alumne','alumnes','legajo','email','mail','correo electronico','e-mail']


def processing_pipeline(df):

    df['text'] = df['text'].apply(correct_paragraphs)
    df['author'] = df.apply(lambda x : get_author(x['text'], x['headers']),axis=1)
    df.loc[df.author.notnull(),'author'] = df[df.author.notnull()]['author'].apply(delete_not_author)
    df['topic'] = df['text'].apply(get_topic)
    df['corpus'] = df['text'].apply(get_corpus)
    df['processed_corpus'] = df['corpus'].apply(process_indexed_corpus)

    return df



def correct_paragraphs(string):
    """
    Corrects the paragraph by validating \n
    """
    string = re.compile('\s*\n').sub('', string, 1)
    string = re.sub('(\w\s)\n\s(\w)', r'\1\2',string)
    return string



def delete_not_author(strings):
    """
    Deletes words that refers to the author but are not the author name or surname
    """
    new_string=[]

    for string in strings:

        #Check if the string is not a messy author string or an email
        if not(any(word in string.lower() for word in messy_author_strings) or any(char.isdigit() for char in string) or re.match('^[\w\.-]+@[\w\.-]+\.\w+$',string)):

            new_string.append(string)

    return new_string if new_string else np.nan





#---Utils-----------------------------------------------------------------------------------------------------
def clean_sentences(string):
    """
    Clean a string from special characters and numbers
    """
    string = re.sub('([a-zA-Z])-([a-zA-Z])', r'\1\2',string)
    string = string.replace('\n',' ')
    string = re.sub('●|•|-|”|“|°|,|/|:|\?|¿|!|¡',' ', string)
    string = string.replace('(',' ').replace(')',' ').replace('[',' ').replace(']',' ').replace('{',' ').replace('}',' ')
    string = re.sub('\d', ' ', string)
    string = re.sub('\s+',' ',string)
    string = string.strip()
    return string


def correct_dots(string):
    """
    Keeps only dots for end of a sentence
    """
    string = re.sub('([a-zA-Z]\s?)\.(\s?[a-z])', r'\1 \2', string)
    string = re.sub('([a-zA-Z]\s?)\.(\s?\))', r'\1 \2', string)
    string = re.sub('(\s[A-Z]\s?)\.(\s?[a-zA-Z])', r'\1 \2', string)
    string = string.replace('\n', ' ')
    return string

def get_corpus(text):
    """
    Get a list of sentences well separated from a text
    """
    text = correct_dots(text)
    corpus = text.split('.')

    return corpus

def process_indexed_corpus(corpus):
    """
    Receive a list of sentences and return a list of cleaned sentences with each index
    """
    processed_corpus = []
    for i, sentence in enumerate(corpus):
        sentence = clean_sentences(sentence)
        sentence = nlp(sentence)
        sentence = [token.lemma_.lower() for token in sentence if not token.is_stop and token.pos_ != 'SPACE' and token.pos_ != 'PUNCT' and len(token.text)>1]
        if len(sentence) > 3:
            sentence = ' '.join(sentence)
            processed_corpus.append((i, sentence))
    return processed_corpus

#---------------------------------------------------------------------------------------------------------------