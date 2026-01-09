import json
import os
from elasticsearch import Elasticsearch, helpers

import pandas as pd

def read_csv_file(file_path):
    """
    Reads a CSV file into a pandas DataFrame.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The DataFrame containing the data from the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully read data from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None

df = pd.read_json('data/airbnb_clean.json', lines=True)

df.to_parquet("airbnb_clean.parquet", index=False)

INPUT_FILE = "data/airbnb_clean.json"
INDEX_NAME = "airbnb-listings"
ES_HOST = "http://localhost:9200"

es = Elasticsearch(ES_HOST, verify_certs=False, ssl_show_warn=False)

if not es.ping():
    print(f"ERREUR CRITIQUE : Impossible de joindre Elasticsearch sur {ES_HOST}")
    print("   -> Vérifiez que votre Docker tourne bien.")
    exit()
else:
    print(f"Connecté au cluster Elasticsearch : {es.info().get('cluster_name')}")

def generate_actions(file_path):
    """
    Lit le fichier JSON ligne par ligne et prépare les actions pour Elasticsearch.
    L'utilisation de 'yield' permet de ne pas charger tout le fichier en mémoire RAM.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                doc = json.loads(line)
                yield {
                    "_index": INDEX_NAME,
                    "_id": str(doc['id']), 
                    "_source": doc
                }
            except Exception as e:
                print(f"Erreur de lecture ligne {i} : {e}")
                pass

# --- 3. EXECUTION ---
if not os.path.exists(INPUT_FILE):
    print(f"ERREUR : Le fichier '{INPUT_FILE}' n'existe pas.")
    print("   -> Avez-vous lancé le script '1_clean_data.py' ?")
    exit()

print(f"Démarrage de l'ingestion depuis : {INPUT_FILE} ...")

try:
    success, failed = helpers.bulk(es, generate_actions(INPUT_FILE), chunk_size=2000)
    
    print("-" * 30)
    print(f" IMPORT TERMINÉ !")
    print(f" ocuments indexés avec succès : {success}")
    
    if len(failed) > 0:
        print(f"Échecs : {len(failed)}")
    else:
        print(f"Zéro erreur. Good job.")
    print("-" * 30)

except Exception as e:
    print(f"Erreur lors de l'envoi : {e}")