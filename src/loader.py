import os
import gdown

files_to_download = {
    "saas_docs.csv":         "https://drive.google.com/file/d/1RElOhN7bYsDAJUNQhYyqM7IzX-Xo6myq/view?usp=sharing",
    "credit_card_terms.csv": "https://drive.google.com/file/d/1_giivc_B0urOKpct0XY2yVZuxW3Eenuf/view?usp=sharing",
    "hospital_policy.csv":   "https://drive.google.com/file/d/1pL7OnDhnmz9pteIpBJ12gu2_ixrc2hPm/view?usp=sharing",
    "ecommerce_faqs.csv":    "https://drive.google.com/file/d/1O4fTjsLFbz55oOiwJUwLwZryO5OSSF6p/view?usp=sharing"
}

def get_files():
    print("--- Downloading Files from Google Drive ---")
    for filename, url in files_to_download.items():
        if not os.path.exists(filename):
            gdown.download(url, filename, quiet=False) # , fuzzy=True
            print(f"Downloaded: {filename}")
        else:
            print(f"Skipped: {filename} (Already exists)")
    print("--- Download Complete ---\n")