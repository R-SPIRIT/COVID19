import math
import pickle
from tqdm import tqdm
from datetime import datetime
from pymongo import MongoClient
from collections import Counter

from konlpy.tag import Okt; okt = Okt()
from ckonlpy.tag import Twitter; spliter = Twitter()

def AddWord(add_word, pos):
    spliter.add_dictionary(add_word, pos)
    
def Tokenize_list(docs_list):
    # must input list [ , ] type
    tokenize_ = []
    for doc_ in docs_list:
        tokenize_.append(spliter.nouns(doc_))
        # tokenize_.append(spliter.morphs(doc_))  
    return tokenize_

def Tokenize_list_morphs(docs_list):
    # must input list [ , ] type
    tokenize_ = []
    for doc_ in docs_list:
        tokenize_.append(spliter.nouns(doc_))
        # tokenize_.append(spliter.morphs(doc_))  
    return tokenize_

  
def Tokenize_dict(docs_dict, keyname = 'content'):
    # must input list [{}, {}] type
    tokenize_ = []
    for doc_ in docs_dict:
        doc_[keyname] = spliter.nouns(doc_[keyname])
        tokenize_.append(doc_)
    return tokenize_

def Stopwords_onelen_Check(Tokenize, display_number = -1):
    tokenize_ = Tokenize.copy()
    with open('./stopword_nowmoment.pkl', 'rb') as f:
        stopn_list = pickle.load(f)
    remove_words = []
    for num_i, doc in enumerate(tokenize_):        
        for num_j ,target_word in enumerate(doc):
            if target_word in stopn_list or len(target_word) == 1:
                remove_words.append((target_word ,num_i ,num_j ))
    print(remove_words)
    remove_words.reverse()
    print(remove_words)
    for r_word in remove_words:
        print(r_word)
        del tokenize_[r_word[1]][r_word[2]]
    if display_number != 0:
        print('제거된 단어 :', remove_words[:display_number])
    return Tokenize

def ck_threshold(count, threshold = 1):
    out_dict = {k:v for k, v in dict(count).items() if v > threshold}            
    return out_dict

def Tfidf(tokenize, pass_title):
    out_dict = {}
    for sum_dict in tokenize:
        make_total_word_list = []
        for n in tokenize[sum_dict]:
    #         print(n)
            make_total_word_list.extend(tokenize[sum_dict][n])

        make_total_word_list = list(set(make_total_word_list))


        idx_word_dict = {}
        word_idx_dict = {}
        for idx, n in enumerate(make_total_word_list[:]):
        #     print(idx)
            idx_word_dict[idx] = n
            word_idx_dict[n] = idx

        total_output_dict = {}
        for t_idx in tokenize[sum_dict]:
            mid_list = []
            for make_idx in tokenize[sum_dict][t_idx]:
                mid_list.append(word_idx_dict[make_idx])
            total_output_dict[t_idx] = mid_list

        out_dict[sum_dict] = total_output_dict
    tokenize = out_dict
    
    each_company = {}
    
    for i in tokenize:
        print(i)
        if i not in pass_title:
            token_ = tokenize[i]
            each_company.update({i:{}})
        #     print(len(token_.keys()))
            finish_conunt = 0
            tf_idf_days = {}
            for idx_day in tqdm(token_.keys()):
                # TF
                count = ck_threshold(Counter(token_[idx_day]))
#                 print(count)
                TF = {}
                for cnoun in count.keys():
                    TF[cnoun] = count[cnoun]/len(token_[idx_day])

                # DF
                DF = {}
                for cnoun in count.keys():
                    DF[cnoun] = 0
                for cnoun in count.keys():
                    for i1 in list(token_.keys()):
                        df_value = set(token_[i1]) & {cnoun}
                        if df_value != set():
                            DF[cnoun] += 1

                # TF-IDF           
                TF_IDF = {}
                for i2 in count.keys():
                    # IDF
                    IDF = math.log(1+len(token_)/(1+DF[i2]))
                    # TF * IDF
                    TF_IDF[i2] = TF[i2] * IDF
            #     result = list(TF_IDF.values())

                # sort and reverse
                sorted_by_value = sorted(TF_IDF.items(), key=lambda kv: kv[1])
                sorted_by_value.reverse()

                tf_idf_days[idx_day] = sorted_by_value[:]
            each_company[i] = tf_idf_days
            
    result_dict = {}
    
    for name in each_company.keys():
        mid_result_dict = {}
        for find_index in each_company[name].keys():
            mid_list = []
            for to_word in each_company[name][find_index]:
                mid_list.append((idx_word_dict[to_word[0]], to_word[1]))
            mid_result_dict[find_index] = mid_list
        result_dict[name] = mid_result_dict
        
    return result_dict



    