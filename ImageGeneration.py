# Backend/ImageGeneration.py
import os
import re
from time import sleep
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image
import requests
import traceback

# Load env
load_dotenv()

# Config
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "Data")
IFILE = os.path.join("Frontend", "Files", "ImageGeneration.data")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(IFILE), exist_ok=True)

# Get HF key
HF_KEY = os.getenv("HuggingFaceAPIKey")
if not HF_KEY:
    print("ERROR: HuggingFaceAPIKey missing in .env. Add HuggingFaceAPIKey=hf_xxx")
    raise SystemExit(1)

# Create client (may be older/newer version)
client = InferenceClient(api_key=HF_KEY)

def sanitize_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in s).strip().replace(" ", "_")

def open_images(prompt):
    prompt_safe = sanitize_filename(prompt)
    for i in range(1, 5):
        path = os.path.join(DATA_DIR, f"{prompt_safe}{i}.png")
        if not os.path.exists(path):
            print("File not found:", path)
            continue
        try:
            img = Image.open(path)
            print("Opening:", path)
            img.show()
            sleep(1)
        except Exception as e:
            print("Unable to open", path, ":", e)

# -------------------------
# Version-safe generator:
# 1) Try client.text_to_image(prompt, model=model) without options kwarg.
# 2) If that fails, fallback to router.huggingface.co via requests.post
# -------------------------
def generate_images_with_client(prompt: str, count: int = 4, model: str = "stabilityai/stable-diffusion-xl-base-1.0"):
    prompt_safe = sanitize_filename(prompt)
    saved = []

    for i in range(count):
        out_path = os.path.join(DATA_DIR, f"{prompt_safe}{i+1}.png")

        # Try InferenceClient.text_to_image (without options kwarg)
        try:
            if hasattr(client, "text_to_image"):
                print(f"Using InferenceClient.text_to_image() for image {i+1}/{count}")
                # Do NOT pass options kwarg here (some versions reject it)
                img = client.text_to_image(prompt, model=model)
                if isinstance(img, bytes):
                    with open(out_path, "wb") as f:
                        f.write(img)
                    saved.append(out_path)
                    print("Saved (bytes):", out_path)
                elif hasattr(img, "save"):
                    img.save(out_path)
                    saved.append(out_path)
                    print("Saved (PIL):", out_path)
                else:
                    print("text_to_image returned unexpected type:", type(img))
        except Exception as e:
            print("text_to_image() failed (will fallback). Error:", e)

        if os.path.exists(out_path):
            continue  # success via client

        # Fallback: call HF router endpoint using requests
        try:
            print(f"FALLBACK -> calling HF router for image {i+1}/{count}")
            router_url = f"https://router.huggingface.co/hf-inference/models/{model}"
            headers = {"Authorization": f"Bearer {HF_KEY}"}
            payload = {
                "inputs": prompt,
                "parameters": {"width": 1024, "height": 1024, "num_inference_steps": 28},
                "options": {"wait_for_model": True}
            }
            resp = requests.post(router_url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 200:
                # write returned bytes
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                saved.append(out_path)
                print("Saved (router fallback):", out_path)
            else:
                print("HF router error:", resp.status_code, resp.text)
        except Exception as e2:
            print("Router fallback failed:", e2)

    return saved

def GenerateImages(prompt: str):
    saved = generate_images_with_client(prompt)
    if saved:
        open_images(prompt)
    else:
        print("No images were generated.")

def main_loop():
    print("Image generator started. Monitoring", IFILE)
    while True:
        try:
            if not os.path.exists(IFILE):
                with open(IFILE, "w") as f:
                    f.write(" ;False")
                sleep(1)
                continue

            with open(IFILE, "r") as f:
                Data = f.read().strip()

            # Flexible split: accept ; or , or :
            parts = re.split(r'[;,:\n]', Data, maxsplit=1)
            if len(parts) == 2:
                Prompt, Status = parts[0].strip(), parts[1].strip()
            else:
                print("Data file format incorrect. Expected 'prompt;True' or similar ->", repr(Data))
                sleep(1)
                continue

            if Status.lower() == "true":
                if not Prompt:
                    print("Empty prompt, skipping.")
                else:
                    print("Generating Images for prompt:", Prompt)
                    try:
                        GenerateImages(prompt=Prompt)
                    except Exception:
                        print("Error during GenerateImages:\n", traceback.format_exc())

                # Reset the status (keep prompt)
                with open(IFILE, "w") as f:
                    f.write(f"{Prompt};False")
            else:
                sleep(1)

        except Exception:
            print("Exception in main loop:\n", traceback.format_exc())
            sleep(1)

if __name__ == "__main__":
    main_loop()
# Backend/ImageGeneration.py
import os
import re
from time import sleep
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image
import requests
import traceback

# Load env
load_dotenv()

# Config
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "Data")
IFILE = os.path.join("Frontend", "Files", "ImageGeneration.data")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(IFILE), exist_ok=True)

# Get HF key
HF_KEY = os.getenv("HuggingFaceAPIKey")
if not HF_KEY:
    print("ERROR: HuggingFaceAPIKey missing in .env. Add HuggingFaceAPIKey=hf_xxx")
    raise SystemExit(1)

# Create client (may be older/newer version)
client = InferenceClient(api_key=HF_KEY)

def sanitize_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in s).strip().replace(" ", "_")

def open_images(prompt):
    prompt_safe = sanitize_filename(prompt)
    for i in range(1, 5):
        path = os.path.join(DATA_DIR, f"{prompt_safe}{i}.png")
        if not os.path.exists(path):
            print("File not found:", path)
            continue
        try:
            img = Image.open(path)
            print("Opening:", path)
            img.show()
            sleep(1)
        except Exception as e:
            print("Unable to open", path, ":", e)

# -------------------------
# Version-safe generator:
# 1) Try client.text_to_image(prompt, model=model) without options kwarg.
# 2) If that fails, fallback to router.huggingface.co via requests.post
# -------------------------
def generate_images_with_client(prompt: str, count: int = 4, model: str = "stabilityai/stable-diffusion-xl-base-1.0"):
    prompt_safe = sanitize_filename(prompt)
    saved = []

    for i in range(count):
        out_path = os.path.join(DATA_DIR, f"{prompt_safe}{i+1}.png")

        # Try InferenceClient.text_to_image (without options kwarg)
        try:
            if hasattr(client, "text_to_image"):
                print(f"Using InferenceClient.text_to_image() for image {i+1}/{count}")
                # Do NOT pass options kwarg here (some versions reject it)
                img = client.text_to_image(prompt, model=model)
                if isinstance(img, bytes):
                    with open(out_path, "wb") as f:
                        f.write(img)
                    saved.append(out_path)
                    print("Saved (bytes):", out_path)
                elif hasattr(img, "save"):
                    img.save(out_path)
                    saved.append(out_path)
                    print("Saved (PIL):", out_path)
                else:
                    print("text_to_image returned unexpected type:", type(img))
        except Exception as e:
            print("text_to_image() failed (will fallback). Error:", e)

        if os.path.exists(out_path):
            continue  # success via client

        # Fallback: call HF router endpoint using requests
        try:
            print(f"FALLBACK -> calling HF router for image {i+1}/{count}")
            router_url = f"https://router.huggingface.co/hf-inference/models/{model}"
            headers = {"Authorization": f"Bearer {HF_KEY}"}
            payload = {
                "inputs": prompt,
                "parameters": {"width": 1024, "height": 1024, "num_inference_steps": 28},
                "options": {"wait_for_model": True}
            }
            resp = requests.post(router_url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 200:
                # write returned bytes
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                saved.append(out_path)
                print("Saved (router fallback):", out_path)
            else:
                print("HF router error:", resp.status_code, resp.text)
        except Exception as e2:
            print("Router fallback failed:", e2)

    return saved

def GenerateImages(prompt: str):
    saved = generate_images_with_client(prompt)
    if saved:
        open_images(prompt)
    else:
        print("No images were generated.")

def main_loop():
    print("Image generator started. Monitoring", IFILE)
    while True:
        try:
            if not os.path.exists(IFILE):
                with open(IFILE, "w") as f:
                    f.write(" ;False")
                sleep(1)
                continue

            with open(IFILE, "r") as f:
                Data = f.read().strip()

            # Flexible split: accept ; or , or :
            parts = re.split(r'[;,:\n]', Data, maxsplit=1)
            if len(parts) == 2:
                Prompt, Status = parts[0].strip(), parts[1].strip()
            else:
                print("Data file format incorrect. Expected 'prompt;True' or similar ->", repr(Data))
                sleep(1)
                continue

            if Status.lower() == "true":
                if not Prompt:
                    print("Empty prompt, skipping.")
                else:
                    print("Generating Images for prompt:", Prompt)
                    try:
                        GenerateImages(prompt=Prompt)
                    except Exception:
                        print("Error during GenerateImages:\n", traceback.format_exc())

                # Reset the status (keep prompt)
                with open(IFILE, "w") as f:
                    f.write(f"{Prompt};False")
            else:
                sleep(1)

        except Exception:
            print("Exception in main loop:\n", traceback.format_exc())
            sleep(1)

if __name__ == "__main__":
    main_loop()
