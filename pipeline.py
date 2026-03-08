import requests
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def extract():
    logging.info("Extracting data from Brewery API...")
    url = "https://api.openbrewerydb.org/v1/breweries?per_page=200"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    logging.info(f"Extracted {len(df)} rows")
    return df

def transform(df):
    logging.info("Transforming data...")
    df = df.dropna(subset=['name', 'state'])
    df['brewery_type'] = df['brewery_type'].str.lower().str.strip()
    df['extracted_at'] = pd.Timestamp.now()
    df = df[['id','name','brewery_type','city','state','country','extracted_at']]
    logging.info(f"After cleaning: {len(df)} rows")
    return df

def load(df, engine):
    logging.info("Loading data into PostgreSQL...")
    # Use engine directly (not connection) - works with all pandas versions
    df.to_sql('breweries', engine, if_exists='replace', index=False)
    logging.info(f"Loaded {len(df)} rows successfully!")

if __name__ == "__main__":
    engine = create_engine("postgresql:///dedb")
    load(transform(extract()), engine)