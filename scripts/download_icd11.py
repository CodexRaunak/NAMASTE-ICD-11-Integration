import os
import requests

URL = "https://drive.google.com/uc?export=download&id=1MuNfO5hmaF5v8aSGloMGyLSbjDEjPXqs"
OUT_PATH = "data/ICD-11.csv"

os.makedirs("data", exist_ok=True)

if not os.path.exists(OUT_PATH):
    print(f"Downloading ICD-11.csv from {URL} ...")
    r = requests.get(URL)
    with open(OUT_PATH, "wb") as f:
        f.write(r.content)
    print("Download complete.")
else:
    print("ICD-11.csv already exists, skipping download.")
