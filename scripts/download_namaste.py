import os
import requests

def download_namaste():
    os.makedirs("data", exist_ok=True)

    NAMASTE_FILES = {
        "namaste_siddha_morbidity.csv": "1cAZtDQGXj-BnOaw5yPbhJSU7l853n3Bx",
        "namaste_unani_morbidity.csv": "1uwvZIjzEPcp2ikuUkEDRgxI0uDWsefSF",
        "namaste_ayurveda_morbidity.csv":"1WXjXo5PAgwSEYqLvx9w-SW3p3Eg7EBx1",
        "ayurveda_standard_terminology.csv": "10q1z9JkSie_Pfr2EzCBDpfF9NkidFzVC",
        "siddha_standard_terminology.csv":"1VRMD1nHG-oNtLEAxr-szy5-swc4AWt_7",
        "siddha_standard_terminology_index.csv":"1sSAqE6okJNgxB9J2h2VoxC3hOn0hAI0p",
        "unani_standard_terminology.csv":"15mOnuyYCV9ix9yyxS_xemb7HtpXJKkaa",
        "unani_standard_terminology_index.csv":"1G1DBBkfSJl-CyEEZHxSQv6yVk9siL"
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

