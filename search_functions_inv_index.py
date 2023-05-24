import math
import re
from collections import Counter
import pymorphy3
from nltk.corpus import stopwords
from BitVector import BitVector

morph = pymorphy3.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))

def normalize_text(text):
    text = re.sub(r'[^\w\t]+', ' ', text)
    text = text.lower()
    words = text.split()
    words = [morph.parse(word)[0].normal_form for word in words]
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
    t=t[2*L+1:] 
    t.insert(0,'1') 
    t.reverse()
    n=0
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
    x = x[K:2*K+1]
  
    n = 0
    x.reverse()
    for i in range(len(x)):
        if x[i] == '1':
            n = n+math.pow(2, i)
    return int(n)

def decompress(index):
    decompressed_index = {}
    for term in index:
        doc_ids = []
        for doc in index[term]:
            doc_ids.append(int(doc))
        decompressed_index[term] = doc_ids
    return decompressed_index

def decompress_gamma(index):
    decompressed_index = {}
    for term in index:
        decompressed_gamma_str = str(index[term])
        numbers = []
        start = 0
        while start < len(decompressed_gamma_str):
            unary_end = decompressed_gamma_str.find('1', start) 
            if unary_end == -1:
                break
            length = unary_end - start + 1 
            number = Elias_Gamma_Decoding(decompressed_gamma_str[start: unary_end + length])
            numbers.append(number)
            start = unary_end + length    
        decompressed_index[term] = numbers

    return decompressed_index

def decompress_delta(index):
    decompressed_delta= {}
    for term in index:
        compressed_delta_str = index[term]
        docs = []
        i = 0
        last_decoded = 0
        while i < len(compressed_delta_str):
            zeros = 0
            while True:
                try: compressed_delta_str[i:i+1]
                except: break
                if (compressed_delta_str[i:i+1] == BitVector(intVal=1)):
                    break
                zeros += 1
                i += 1
            if len(compressed_delta_str) > 1 : i+= 1
            next_m_bits = BitVector(size=0)
            for j in range(zeros):
                try:  next_m_bits += compressed_delta_str[i:i+1]
                except: break
                i += 1
            l_value = 2 ** zeros + next_m_bits.intValue()
            next_l_bits = BitVector(size=0)
            for j in range(l_value - 1):
                try: next_l_bits += compressed_delta_str[i:i+1]
                except: break
                i += 1
            value = 2 ** (l_value - 1) + next_l_bits.intValue()
            value += last_decoded
            last_decoded = value
            docs.append(value)
        decompressed_delta[term] = docs
    return decompressed_delta


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
    if len(query_words) == 0:
        return('Stopword')
    try: result_docs = delta_decode([Elias_Gamma_Decoding(doc) for doc in index[query_words[0]]])
    except KeyError: return('Not Found') 
    if len(query_words) == 1: return result_docs
    for word in query_words:
        word_docs = Counter(delta_decode([Elias_Gamma_Decoding(doc) for doc in list(index[word])]))
        result_docs = list((Counter(result_docs) & word_docs).elements())
    
    return result_docs


def delta_search(query, index):
    query_words = normalize_text(query)
    if len(query_words) == 0:
        return('Stopword')
    try: result_docs = delta_decode([Elias_Delta_Decoding(doc) for doc in list(index[query_words[0]])])
    except KeyError: return('Not Found') 
    if len(query_words) == 1: return result_docs
    for word in query_words:
        word_docs = Counter(delta_decode([Elias_Delta_Decoding(doc) for doc in list(index[word])]))
        result_docs = list((Counter(result_docs) & word_docs).elements())
    
    return result_docs


def index_search_BitVector_decode(query, index):
    index = decompress(index)
    query_words = normalize_text(query)
    if len(query_words) == 0:
        return('Stop word')
    try: result_docs = set(delta_decode(index[query_words[0]]))
    except KeyError: return('Not Found') 
    for word in query_words:
        result_docs = result_docs.intersection(delta_decode(index[word]))
    return result_docs


def gamma_search_BitVector_decode(query, index):
    index = decompress_gamma(index)
    query_words = normalize_text(query)
    if len(query_words) == 0:
        return('Stopword')
    try: result_docs = set(delta_decode(index[query_words[0]]))
    except KeyError: return('Not Found') 
    if len(query_words) == 1: return result_docs
    for word in query_words:
        result_docs = result_docs.intersection(delta_decode(index[word]))
    return result_docs


def delta_search_BitVector_decode(query, index):
    index = decompress_delta(index)
    query_words = normalize_text(query)
    if len(query_words) == 0:
        return('Not found')
    try: res = set(delta_decode(index[query_words[0]]))
    except KeyError: return('Not Found') 
    if len(query_words) == 1: return res
    for word in query_words:
        res = res.intersection(delta_decode(index[word]))
    return res