import os
import requests

def download_namaste():
    os.makedirs("data", exist_ok=True)

    NAMASTE_FILES = {
        "namaste_siddha_morbidity.csv": "1cAZtDQGXj-BnOaw5yPbhJSU7l853n3Bx",
        "namaste_ayurveda_morbidity.csv": "1dXf1U1a4dn3Ctuj1nhlQvVHeYPzIarxB"
    }

    BASE_URL = "https://drive.google.com/uc?export=download&id={file_id}"

    for filename, file_id in NAMASTE_FILES.items():
        out_path = os.path.join("data", filename)
        if not os.path.exists(out_path):
            url = BASE_URL.format(file_id=file_id)
            print(f"Downloading {filename} from {url} ...")
            try:
                r = requests.get(url)
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded {filename}")
            except requests.RequestException as e:
                print(f"Failed to download {filename}: {e}")
        else:
            print(f"{filename} already exists, skipping.")