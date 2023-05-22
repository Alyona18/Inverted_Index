from collections import defaultdict
import math
import re
from math import log
from math import floor

def delta_encode(buffer):
    last = 0
    delta = []
    for i in range(len(buffer)):
        current = buffer[i]
        delta.append(current - last)
        last = current
    return delta

def Binary_Representation_Without_MSB(x):
	binary = "{0:b}".format(int(x))
	binary_without_MSB = binary[1:]
	return binary_without_MSB

def EliasGammaEncode(k):
	if (k == 0):
		return '0'
	if (k == 1):
		return '1'
	N = 1 + floor(log(k,2))
	Unary = (N-1)*'0'+'1'
	return Unary + Binary_Representation_Without_MSB(k)

def EliasDeltaEncode(x):
	if x==0: Gamma = EliasGammaEncode(0)
	else: Gamma = EliasGammaEncode(1 + floor(log(x,2)))
	binary_without_MSB = Binary_Representation_Without_MSB(x)
	return Gamma+binary_without_MSB

log2 = lambda x: log(x, 2)

def Unary(x):
	return (x-1)*'0'+'1'

def Binary(x, l = 1):
	s = '{0:0%db}' % l
	return s.format(x)
	
def Elias_Gamma(x):
	if(x == 0):
		return '0'

	n = 1 + int(log2(x))
	b = x - 2**(int(log2(x)))

	l = int(log2(x))

	return Unary(n) + Binary(b, l)

def inverted_index(tokens_list):
    # Создаем пустой словарь для инвертированного индекса
    inverted_index_dict = defaultdict(list)
    
    # Проходимся по всем документам в списке токенов
    for doc_id, tokens in enumerate(tokens_list):
        # Проходимся по всем токенам в документе
        for token in tokens:
            # Добавляем документ в список документов для данного токена
            inverted_index_dict[token].append(doc_id)
    
    # Проходимся по всем ключам (термам) инвертированного индекса
    delta_index = {}


    for term in inverted_index_dict:
    # Создаем список для дельта-кодированных позиций
        delta_index[term] = delta_encode(inverted_index_dict[term])
    # Возвращаем инвертированный индекс в виде словаря
    return dict(delta_index)


def inverted_index_with_gamma(index):
    
    gamma_index = {}

    for term in index:
         gamma_values = []
         for n in index[term]:
             gamma_values.append(Elias_Gamma(n))
         gamma_index[term] = gamma_values
    return dict(gamma_index)

def inverted_index_with_delta(index):

    delta_elias_index = {}
    
    for term in index:
         delta_elias_values = []
         for n in index[term]:
             delta_elias_values.append(EliasDeltaEncode(n))
         delta_elias_index[term] = delta_elias_values
    return dict(delta_elias_index)
