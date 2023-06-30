from plagiarism_detection import threshold
from helper import pd
from topic import google_topic
from reader import read_urls
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_similarities(df, comparing_df):

    similarities = {}

    db_similarities(df[['corpus','processed_corpus']], comparing_df, similarities)

    if df['citations'] == True:
        url_similarities(df[['corpus', 'processed_corpus']], df['citations'], similarities)
        
    googled_topic_similarities(df[['corpus', 'processed_corpus']],df['topic'], similarities)
    return similarities

def db_similarities(df, comparing_df, similarities):
    
    unprocessed_corpus = df['corpus']
    processed_corpus = df['processed_corpus']
    
    corpus = [slice[1] for slice in processed_corpus]
    
    for _, row in comparing_df.iterrows():


        row_unprocessed_corpus = row['corpus']
        row_indexed_corpus = row['processed_corpus']
        row_corpus = [slice[1] for slice in row_indexed_corpus]

        vectorizer = CountVectorizer()
        vectorizer.fit(row_corpus + corpus)

        for slice in processed_corpus:
            index, sentence = slice
            
            plagiarism = []
            for row_slice in row_indexed_corpus:
                row_index, row_sentence = row_slice
                vector = vectorizer.transform([row_sentence, sentence])
                score = cosine_similarity(vector)[0][1]
                if 0.99 > score > threshold:
                    plagiarism.append({'plagiarized_sentence':row_unprocessed_corpus[row_index],
                                       'plagiarism_score':score, 
                                       'plagiarized_file':row['filename'],  
                                       'plagiarized_author':row['author'] 
                                      })
            if len(plagiarism) > 0:
                append_to_dictionary(similarities, unprocessed_corpus[index], index, plagiarism)
                    
    return similarities

def url_similarities(df, urls, similarities):
    

    unprocessed_corpus = df['corpus']
    processed_corpus = df['processed_corpus']
    
    comparing_df = read_urls(urls)

    corpus = [slice[1] for slice in processed_corpus]
    
    for _, row in comparing_df.iterrows():


        row_unprocessed_corpus = row['corpus']
        row_indexed_corpus = row['processed_corpus']
        row_corpus = [slice[1] for slice in row_indexed_corpus]

        vectorizer = CountVectorizer()
        vectorizer.fit(row_corpus + corpus)

        for slice in processed_corpus:
            index, sentence = slice
            
            plagiarism = []
            for row_slice in row_indexed_corpus:
                row_index, row_sentence = row_slice
                vector = vectorizer.transform([row_sentence, sentence])
                score = cosine_similarity(vector)[0][1]
                if 0.99 > score > threshold:
                    plagiarism.append({'plagiarized_sentence':row_unprocessed_corpus[row_index],
                                      'plagiarism_score':score, 
                                      'plagiarized_website':row['url'] 
                                      })
            if len(plagiarism) > 0:
                append_to_dictionary(similarities, unprocessed_corpus[index], index, plagiarism)
                    
    return similarities
    
def googled_topic_similarities(df, topic):
    
    urls = google_topic(topic)
    return url_similarities(df, urls)

def append_to_dictionary(dic, key, index, element):
    dic.setdefault(key, {'n_sentence': index, 'plagiarism': []})
    dic[key]['plagiarism'] += element