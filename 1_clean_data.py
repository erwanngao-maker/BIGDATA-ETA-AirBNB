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

def write_csv_file(df, file_path, index=False):
    """
    Writes a pandas DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        file_path (str): The path to the output CSV file.
        index (bool): Whether to write the DataFrame index as a column.
    """
    try:
        df.to_csv(file_path, index=index)
        print(f"Successfully wrote data to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")

lyon_df = read_csv_file('data/listings_lyon.csv')
paris_df = read_csv_file('data/listings_paris.csv')
bordeaux_df = read_csv_file('data/listings_bordeaux.csv')
lyon_df["target_city"] = "Lyon"
paris_df["target_city"] = "Paris"
bordeaux_df["target_city"] = "Bordeaux"

df = pd.concat([lyon_df, paris_df, bordeaux_df], ignore_index=True)

df["location"] = (
    df["latitude"].astype(str) + "," + df["longitude"].astype(str)
)

# Petit 3 — Nettoyage de la colonne "price"

df["price"] = (
    df["price"]
    .astype("string")
    .str.strip()
    .str.replace("$", "", regex=False)
    .str.replace("€", "", regex=False)
    .str.replace(",", "", regex=False)
)

df["price"] = pd.to_numeric(df["price"], errors="coerce")

# Suppression des lignes avec des valeurs nulles dans price
df = df.dropna(subset=["price"])

df.to_json('data/airbnb_clean.json', orient='records', lines=True)