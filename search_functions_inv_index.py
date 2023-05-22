from collections import defaultdict
import math
import re
from collections import Counter
from collections import defaultdict
import pymorphy3
from nltk.corpus import stopwords

morph = pymorphy3.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))

def normalize_text(text):
    # удаление знаков препинания и других неалфавитных символов
    text = re.sub(r'[^\w\t]+', ' ', text)
    # приведение к нижнему регистру
    text = text.lower()
    # разбиение текста на слова
    words = text.split()
    # лемматизация слов
    words = [morph.parse(word)[0].normal_form for word in words]
    # удаление стоп-слов
    words = [word for word in words if word not in stop_words]

    words = list(set(words))
    return words


def delta_decode(buffer):
    last = 0
    d = buffer
    for i in range(len(buffer)):
        delta = d[i]
        d[i] = delta + last
        last = d[i]
    return d

def  Elias_Delta_Decoding(x):
    t = list(x)
    if len(t) == 1 and t[0] == '0':
        return 0
    if len(t) == 1 and t[0] == '1':
        return 1
    L=0    
    while True:
        if not t[L] == '0':
            break
        L= L + 1
      
    # Reading L more bits and dropping ALL
    t=t[2*L+1:] 
      
    # Prepending with 1 in MSB
    t.insert(0,'1') 
    t.reverse()
    n=0
      
    # Converting binary to integer
    for i in range(len(t)): 
        if t[i]=='1':
            n=n+math.pow(2,i)
    return int(n)
  

def Elias_Gamma_Decoding(x):
    x = list(x)
    if len(x) == 1:
        return 0
    K = 0
    while True:
        if not x[K] == '0':
            break
        K = K + 1
      
    # Reading K more bits from '1'
    x = x[K:2*K+1]
  
    n = 0
    x.reverse()
      
    # Converting binary to integer
    for i in range(len(x)):
        if x[i] == '1':
            n = n+math.pow(2, i)
    return int(n)


def index_search(query, index):
    query_words = normalize_text(query)
    if len(query_words) == 0:
        return('Stop word')
    try: result_docs = index[query_words[0]]
    except KeyError: return('Not Found') 
    for word in query_words:
        result_docs = list((Counter(result_docs) & Counter(index[word])).elements())
    result_docs = delta_decode(result_docs)

    return result_docs

def gamma_search(query, index):
    query_words = normalize_text(query)
    index[query_words[0]]
    if len(query_words) == 0:
        return('Not found')
    try: result_docs = index[query_words[0]]
    except KeyError: return('Not Found') 
    for word in query_words:
        result_docs = list((Counter(result_docs) & Counter(index[word])).elements())
    result_docs = delta_decode([Elias_Gamma_Decoding(doc) for doc in list(result_docs)])

    return result_docs


def delta_search(query, index):
    query_words = normalize_text(query)
    if len(query_words) == 0:
        return('Not found')
    try: result_docs = index[query_words[0]]
    except KeyError: return('Not Found') 
    for word in query_words:
        result_docs = list((Counter(result_docs) & Counter(index[word])).elements())
    result_docs = delta_decode([Elias_Delta_Decoding(doc) for doc in list(result_docs)])

    return result_docs
