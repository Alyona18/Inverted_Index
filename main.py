import search_functions_inv_index as search
import create_functions_inv_index as create
import json
import pandas as pd


query = input("Mode (1 - new, 2 - previous index): ")

if query == '1': 
    df = pd.read_csv("C:/Users/Alyonka/Documents/spbu_docs_clean.csv")
    df.head()

    df_mini =  df.head(500)

    inverted_index_dict = create.inverted_index(df_mini.text.apply(search.normalize_text))
    inverted_index_gamma = create.inverted_index_with_gamma(inverted_index_dict)
    inverted_index_delta = create.inverted_index_with_delta(inverted_index_dict)

    with open ("index2.json", 'w') as f:
           json.dump(inverted_index_dict, f)
           f.close()
else:
    with open ("index.json", 'r') as f:
        inverted_index_dict = json.load(f)
        f.close()

    inverted_index_gamma = create.inverted_index_with_gamma(inverted_index_dict)
    inverted_index_delta = create.inverted_index_with_delta(inverted_index_dict)


query = input("Введите запрос: ")

#Just Inverted Index

result_docs = search.index_search(query, inverted_index_dict)
print(result_docs)

# Inverted with delta

result_docs = search.delta_search(query, inverted_index_delta)
print(result_docs)

# Inverted with gamma

result_docs = search.gamma_search(query, inverted_index_gamma)
print(result_docs)

