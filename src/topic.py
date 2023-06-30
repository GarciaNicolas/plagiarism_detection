from plagiarism_detection import closeness
from helper import nlp
from collections import Counter
from processor import clean_sentences
from googlesearch import search


def get_topic(text):
    """
    Get the most common words in a corpus
    """
    text = clean_sentences(text)
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.pos_ != 'SPACE' and token.pos_ != 'PUNCT' and len(token.text)>1]
    topic = Counter(tokens).most_common(10)
    topic = [token[0] for token in topic]
    return topic

def google_topic(topic):
    """
    Look for topics in google and return the first 3 results
    """
    query = ' '.join(topic)

    #The list is sliced because the function sometimes returns more than 3 results
    urls = [url for url in search(query, num_results=3)][0:3]
    return urls

def similar_topics(df, comparing_df):
    """
    Compare the topics of two dataframes and return the ones that have more than x number of topics (closeness) in common
    """
    topic = df['topic']

    #Filtering by the intersection of topics
    filtered_df = comparing_df[comparing_df['topic'].apply(lambda x: len(set(x) & set(topic)) > closeness)]

    return filtered_df