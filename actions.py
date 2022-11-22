import re
import string
import numpy as np
import pandas as pd
import textdistance
import time
import os

def process_data(file_name):
    words = []
    with open(file_name, "r") as f:
        data = f.read()
        data_lower = data.lower()
        words = re.findall(r"\w+", data_lower)
    return words

def save_vocab():
    print(os.getcwd())
    word_l = process_data(os.getcwd()+"/words4.txt")
    vocab = set(word_l)
    print(f"There are {len(vocab)} words in the vocabulary.\n")
    return word_l

def get_count(word_l, word):
    word_count_dict = {}
    for i in range(len(word_l)):
        word_count_dict[word_l[i]] = 1
    return word_count_dict

# fix this function calculations
def get_probabilities(word_count_dict):
    probabilities = {}
    total = sum(word_count_dict.values())
    for i in word_count_dict:
        probabilities[i] = float("{:f}".format(word_count_dict[i] / total))
    return probabilities

def delete_letter(word, verbose=False):
    delete_l = []
    delete_l = [word[0:i] + word[i+1 : len(word)] for i in range(len(word))]
    if verbose:
        print(f"input word = {word}, delete_l = {delete_l}\n")
    return delete_l

def switch_letter(word, verbose=False):
    switch_l = []
    word1 = list(word)
    for i in range(len(word1)-1):
        a1 = list(word1)
        a1[i], a1[i+1] = a1[i+1], a1[i]
        b = "".join(a1)
        switch_l.append(b)
    if word in switch_l:
        switch_l.remove(word)
    if verbose:
        print(f"Input word = {word}, switch_l = {switch_l}\n")
    return switch_l

def replace_letter(word, verbose=False):
    replace_l = []
    replace_set = []
    lower = string.ascii_lowercase
    for i in range(len(word)):
        temp = [word[0:i] + j + word[i+1:len(word)] for j in lower]
        temp.remove(word)
        replace_set.extend(temp)
    replace_l = sorted(list(replace_set))
    if verbose:
        print(f"Input word = {word}, replace_l = {replace_l}\n")
    return replace_l

def insert_letter(word, verbose=False):
    insert_l = []
    lower = string.ascii_lowercase
    for i in range(len(word)+1):
        temp = [word[0:i] + j + word[i:len(word)] for j in lower]
        insert_l.extend(temp)
    if verbose:
        print(f"Input word = {word}, insert_l = {insert_l}")
        print(f"len(insert_l) = {len(insert_l)}\n")
    return insert_l

def edit_1_letter(word):
    edit_1_set = set(delete_letter(word) + insert_letter(word) + replace_letter(word) + switch_letter(word))
    return edit_1_set

def edit_2_letters(word, allow_switches=True):
    edit_2_set = set()
    insert_letter1 = []
    replace_letter1 = []
    switch_letter1 = []
    delete_letter1 = []
    l = list(edit_1_letter(word))
    temp = []
    for i in l:
        temp = delete_letter(i)
        delete_letter1.extend(temp)
    for i in l:
        temp = replace_letter(i)
        replace_letter1.extend(temp)
    for i in l:
        temp = switch_letter(i)
        switch_letter1.extend(temp)
    for i in l:
        temp = insert_letter(i)
        insert_letter1.extend(temp)
    edit_2_set = set(replace_letter1 + switch_letter1 + delete_letter1 + insert_letter1)
    return edit_2_set

def min_edit_distance(source, target, insert_cost=1, delete_cost=1, replace_cost=2):
    a, b, c = 0, 0, 0
    d = []
    len_src = len(source)
    len_target = len(target)
    Dimension = np.zeros((len_src+1, len_target+1), dtype=int)
    for row in range(0, len_src+1):
        Dimension[row, 0] = row
    for col in range(0, len_target+1):
        Dimension[0, col] = col
    for row in range(1, len_src+1):
        for col in range(1, len_target+1):
            r_cost = replace_cost
            if source[row-1] == target[col-1]:
                r_cost = 0
            a = Dimension[row-1, col] + delete_cost
            b = Dimension[row, col-1] + insert_cost
            c = Dimension[row-1, col-1] + r_cost
            d = [a, b, c]
            Dimension[row, col] = min(d)
    minimum_edit_distance = Dimension[len_src, len_target]
    return Dimension, minimum_edit_distance

def similarity(word, word_l):
    # return [textdistance.algorithms.levenshtein.normalized_similarity(v, word) for v in word_l]
    return [1-(textdistance.Jaccard(qval=2).distance(v,word)) for v in word_l]
    # return [(textdistance.Jaccard(qval=2).similarity(v, word)) for v in word_l]

def calculate(word, word_l, probabilities):
    if word in word_l:
        return f"We have {word} in our dictionary."
    else:
        matrix, min_edit, df = [], [], []
        for i in range(len(word_l)):
            matrix_temp, min_edit_temp = min_edit_distance(word, word_l[i])
            matrix.append(matrix_temp)
            min_edit.append(min_edit_temp)
            idx = list("#" + word)
            cols = list("#" + word_l[i])
            df_temp = pd.DataFrame(matrix_temp, index=idx, columns=cols)
            df.append(df_temp)
    
    sim = similarity(word, word_l)
    for i in range(len(min_edit)):
        for j in range(len(min_edit)-1):
            if min_edit[j] > min_edit[j+1]:
                min_edit[j], min_edit[j+1] = min_edit[j+1], min_edit[j]
                word_l[j], word_l[j+1] = word_l[j+1], word_l[j]
                sim[j], sim[j+1] = sim[j+1], sim[j]
                df[j], df[j+1] = df[j+1], df[j]
    
    for i in range(len(min_edit)):
        for j in range(len(min_edit)-1):
            if min_edit[j] == min_edit[j+1] and sim[j] < sim[j+1]:
                min_edit[j], min_edit[j+1] = min_edit[j+1], min_edit[j]
                word_l[j], word_l[j+1] = word_l[j+1], word_l[j]
                sim[j], sim[j+1] = sim[j+1], sim[j]
                df[j], df[j+1] = df[j+1], df[j]
    
    return summary(word_l, sim, probabilities, min_edit)

def summary(word_l, sim,  probs, min_edit=[]):
    df = pd.DataFrame.from_dict(probs, orient='index').reset_index()
    df = df.rename(columns={'index':'Word', 0:'Prob'})
    df['Word'] = word_l
    df['Similarity'] = sim
    if min_edit:
        df['Min Edit'] = min_edit
    if not len(min_edit):
        output = df.sort_values(['Similarity'], ascending=False).head(10)
    else:
        output = df.sort_values(['Min Edit', 'Similarity'], ascending=[True, False]).head(10).reset_index().drop(columns=["index", "Prob"])
    return output