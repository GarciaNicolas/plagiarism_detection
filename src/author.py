from helper import pd, np, nlp, author_synonyms

stop_author = ['legajo', 'email', 'mail', 'correo electronico', 'e-mail']

def first_contiguos_persons(listed_doc):
    """
    Return the start and end index of the first contiguos persons in a list of spacy spans
    """
    try:
        doc_ents = [span.ent_type_ for span in listed_doc]

        #Looks for the index of the first PER entity
        index_start = doc_ents.index('PER')

        #Loop through entities until it finds a non PER entity
        for i, slice in enumerate(doc_ents[index_start:]):
            index_end = index_start + i
            if slice != 'PER':
                break
        return (index_start, index_end)
    
    except:

        #If there are not any PER entities, return -1
        index_start = -1
        index_end = -1
        return (index_start, index_end)

def slice_string(string, author_synonyms):
    """
    Receives a string a return it sliced where the author is supposed to be
    """
    string = string.split('\n')
    i = 0
    while(i<len(string)):
        slice = string[i]
        slice = slice.lower().strip()
        for synonym in author_synonyms:

            #Joining the author synonym is in another line that the author name and we need some context for entities recognition
            if slice.endswith(synonym) or slice.endswith(synonym + ":"):
                return ' '.join(string[i: i+2])
            
            #If the author is in the same line as the synonym
            if synonym in slice:
                return slice
        i +=1
    return ' '.join(string)

def get_author(string, headers):
    """
    Look for authors in a documents and return a list of them.
    If it has trouble finding the author, it a list of first contiguos persons entities.
    Also if there are not any persons entities, it returns np.nan
    """
    string = slice_string(string, author_synonyms)
    author = [] 
    doc = nlp(string)
    author_synonyms = [author for author in author_synonyms if author in doc.text.lower()]

    for i,token in enumerate(doc):

        #If there is any author synonym, look for the first contiguos persons before it
        if token.text.lower() in author_synonyms:
            sliced_doc = doc[i+1:]
            doc_list = [doc for doc in sliced_doc if (doc.text.lower() not in stop_author) and not(doc.pos_ == 'PUNCT' or doc.pos_ == 'SPACE')]
            index = first_contiguos_persons(doc_list)
            author += [doc.text for doc in doc_list[index[0]:index[1]]]

            return author
    
    #If there are not any author synonyms, look into haeders the first contiguos persons
    if author == [] and not (type(headers) == float and pd.isna(headers)):
        
        for header in headers:
            doc = nlp(header)
            for i, token in enumerate(doc):
                if token.text.lower() in author_synonyms:
                    doc = doc[i+1:]
                    doc_list = [token for token in doc if (doc.text.lower() not in stop_author) and not(doc.pos_ == 'PUNCT' or doc.pos_ == 'SPACE')]
                    index = first_contiguos_persons(doc_list)
                    author += [doc.text for doc in doc_list[index[0]:index[1]]]
    elif author == []:

        author = np.nan
    
    return author
