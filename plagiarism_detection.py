import argparse
import json

from src.reader import read_file, read_path, read_database
from src.processor import processing_pipeline
from src.similarity import get_similarities
from src.topic import similar_topics
from src.helper import merge_dataframes


database = True 
threshold = 0.7 
closeness = 3
store = False
comparing_path = ''


def validate_threshold(value):
    if 0 <= value <= 1:
        return value
    raise argparse.ArgumentTypeError("Threshold must be between 0 and 1")

def validate_closeness(value):
    if 0 <= value <= 10:
        return value
    raise argparse.ArgumentTypeError("Closeness must be between 0 and 10")


def plagiarism_detection(file_path):
    """
    Receive a file path and return a json with the similarities.
    """

    #Read the file and store it in a dataframe
    file = read_file(file_path)

    #If comparing_path is not empty, read the files from the path and store them in a dataframe
    if comparing_path:
        comparing_files = read_path(comparing_path)
        comparing_files.apply(processing_pipeline)

        #If database is True, read the database and merge it with the comparing files
        if database:
            comparing_files = merge_dataframes(comparing_files, read_database())

    #If comparing_path is empty and database is True, read the database and store it in a dataframe        
    elif database:
        comparing_files = read_database()
    
    else:
        raise Exception('No files to compare')
    

    file.apply(processing_pipeline)

    #If store is True, update the database with comparing files
    if store:
        comparing_files.to_csv('./data.csv', index=False)

    #Keep only the files with similar topics
    comparing_files = similar_topics(file, comparing_files)

    #Get the similarities between the file and the comparing files
    similarities = get_similarities(file, comparing_files)

    with open('results.json', 'w') as results_file:
        json.dump(similarities, results_file, indent=4, sort_keys=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Plagiarism Detector")

    parser.add_argument("file_path", help="Path to the file to be analyzed")
    parser.add_argument("-p", "--comparing_path",type=str, default='', help="Path to the files to be compared with the analyzed file")
    parser.add_argument("-db", "--database", type=bool, default=True, help="Use files from the database to compare (default: True)")
    parser.add_argument("-t", "--threshold", type=validate_threshold, default=0.7, help="Similarity threshold (default: 0.7)")
    parser.add_argument("-n", "--closeness", type=int, default=3, help="Closeness between topics (default: 0.7)")
    parser.add_argument("-s", "--store", type=bool, default=False, help="Store the used file in the database (default: False)")

    args = parser.parse_args()

    database = args.database
    threshold = args.threshold
    closeness = args.closeness
    store = args.store
    comparing_path = args.comparing_path

    plagiarism_detection(args.file_path)