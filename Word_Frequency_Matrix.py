import os
import re
import os.path
import csv
from nltk.tokenize import WhitespaceTokenizer
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import operator
from collections import Counter, OrderedDict
from itertools import dropwhile
import time
import sys


# set directory (change to your own directory)
os.chdir(os.getcwd())
# Get the NER tags and transform to list
NER_list = pd.read_csv('NER_Tags_Unique.csv', header=0)['Name'].tolist()
# Stop words from nltk library
stop = stopwords.words('english')
# make a list of all names to be deleted in our text analysis
delete_names_all = stop + NER_list
# lower case all our delete_names
delete_names_all_lower = [word.lower() for word in delete_names_all]

# Tokenizization function for our text and eliminates stop word and NER tags (please read Readme File for instructions related to getting the NER tags)


def RunTokenize_One_Text(one_text):
    tokens = WhitespaceTokenizer().tokenize(re.sub("[^a-zA-Z]", " ", one_text))
    good_words_lowerCase = [wd.lower() for wd in tokens]
    good_words = [
        i for i in good_words_lowerCase if i not in delete_names_all_lower and len(i) > 2]
    return good_words

# Generate word dictionnary from our csv input (csv contains two columns)


def get_word_dictionnary(filename):
    synopsis_tokenized = []
    caption_tokenized = []
    file_number = []
    row_count = 0
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_count += 1
            file_number.append(row_count)
            synopsis_tokenized.append(RunTokenize_One_Text(row['synopsis']))
            caption_tokenized.append(RunTokenize_One_Text(row['caption']))
    synopsis_dictionnary = [Counter(words) for words in synopsis_tokenized]
    caption_dictionnary = [Counter(words) for words in caption_tokenized]
    return synopsis_dictionnary, caption_dictionnary

# Get dictionnary (in this case I have a csv file with two columns)


def get_all_dictionnary(synopsis_dictionnary, caption_dictionnary, MaxOccurence):
    bagofwords_ViacomAll = [x for x in synopsis_dictionnary]
    bagofwords_ViacomAll.extend(caption_dictionnary)
    sumbag_viacomAll = sum(bagofwords_ViacomAll, Counter())
    Viacom_dict_clean = Counter(
        dict(filter(lambda x: x[1] >= MaxOccurence, sumbag_viacomAll.items())))
    list_of_words = [k for (k, v) in sorted(
        Viacom_dict_clean.items(), key=operator.itemgetter(1), reverse=True)]
    word_dictionary = {}
    for i in range(len(list_of_words)):
        word_dictionary[list_of_words[i]] = i
    return list_of_words, word_dictionary, Viacom_dict_clean

# Generate concurency matrix


def GenerateMatrix(bagsofwords, output_appendix, list_of_words, word_dictionary):
    total_word_count = len(word_dictionary)
    with open('WordMatrix_' + output_appendix + '_rownum.csv', 'wb') as word_matrix:
        word_matrix.write('RowNum,' + ','.join(list_of_words) + '\n')
        for i in range(len(bagsofwords)):
            onebag = bagsofwords[i]
            word_matrix.write(str(i + 1) + ',')
            listofzeros = [0] * total_word_count
            for key in onebag.keys():
                if key in word_dictionary:
                    column_location = word_dictionary[key]
                    listofzeros[column_location] = onebag[key]
            s = ','.join([str(k) for k in listofzeros])
            word_matrix.write(s)
            word_matrix.write('\n')

# Write time of execution of the program and add anything else (Readme Generator)


def Write_Readme(str1, file_name):
    Readme = open('Readme_%s.txt' % file_name, 'w')
    Readme.write('The program took: %s' % str1)
    Readme.close()


# Input csv file as argument in command line
def main():
    (name, ext) = os.path.splitext(sys.argv[1])
    filename = name + ext
    start_time = time.time()
    (synopsis_dictionnary, caption_dictionnary) = get_word_dictionnary(filename)
    (list_of_words, word_dictionary, Viacom_dict_clean) = get_all_dictionnary(
        synopsis_dictionnary, caption_dictionnary, 100)
    GenerateMatrix(synopsis_dictionnary, 'synopsis',
                   list_of_words, word_dictionary)
    GenerateMatrix(caption_dictionnary, 'caption',
                   list_of_words, word_dictionary)
    all_words_count = pd.DataFrame(
        {'Word': Viacom_dict_clean.keys(), 'Count': Viacom_dict_clean.values()})
    all_words_count.to_csv('all_words_count.csv', columns=[
                           'Word', 'Count'], index=False)
    TotalTime = time.time() - start_time
    Write_Readme(TotalTime, filename)


if __name__ == '__main__':
    main()
