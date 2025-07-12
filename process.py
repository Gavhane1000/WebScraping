import pandas as pd
import re
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
from datetime import datetime
from collections import Counter

# Settings
RAW_FILE = "tweets.csv"
CLEAN_FILE = "data/cleaned.parquet"
TFIDF_MATRIX = "data/tfidf.npz"
SIGNAL_FEATURES = ["buy", "bullish", "long", "target", "sell", "bearish", "short", "stoploss"]

os.makedirs("data", exist_ok=True)

# --- STEP 1: LOAD RAW DATA ---
print("[1] Loading raw data...")
df = pd.read_csv(RAW_FILE)

# --- STEP 2: CLEANING ---
print("[2] Cleaning tweet text...")

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.lower().strip()

df["clean_content"] = df["content"].astype(str).apply(clean_text)

df = df[df["clean_content"].str.strip().astype(bool)]

# --- STEP 3: DEDUPLICATE ---
print("[3] Deduplicating...")
df = df.drop_duplicates(subset=["clean_content"])

# --- STEP 4: HANDLE DATETIME ---
df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

# --- STEP 5: SIGNAL GENERATION ---
print("[4] Generating signals...")

buy_words = {"buy", "bullish", "long", "target"}
sell_words = {"sell", "bearish", "short", "stoploss"}

def classify_signal(text):
    if any(w in text for w in buy_words):
        return 1
    elif any(w in text for w in sell_words):
        return -1
    else:
        return 0

df["signal"] = df["clean_content"].apply(classify_signal)

# --- STEP 6: TF-IDF VECTORIZATION ---
print("[5] Vectorizing (TF-IDF)...")
tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1,2), stop_words="english")
X = tfidf.fit_transform(df["clean_content"])

sparse.save_npz(TFIDF_MATRIX, X)

# --- STEP 7: EXPORT CLEANED DATA ---
print(f"[6] Saving cleaned data to {CLEAN_FILE}")
df.to_csv(CLEAN_FILE.replace(".parquet", ".csv"), index=False)

print(f"[✓] All Done. {len(df)} cleaned tweets processed.")
print(f"Signals: {Counter(df['signal'])}")
