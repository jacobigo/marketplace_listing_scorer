# to run: 
# python -m uvicorn server:app --host 127.0.0.1 --port 8000


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import re
import requests
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = "llava-phi3"    # vision model



class Listing(BaseModel):
    title: str
    price: int
    image: str | None = None

# ollama calling command
def call_ollama(prompt: str, image_path: str | None) -> str:
    cmd = ["ollama", "run", MODEL]

    if image_path:
        cmd.append(image_path)
        print(f"appending image path: {image_path}")
    else:
        print("NO IMAGE PATH (call_ollama)")

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="ignore",
            timeout=60
        )

        print(f"prompt: {prompt}")
        print(f"result: {result}")
        return result.stdout
    except subprocess.TimeoutExpired:
        print("Ollama command timed out.")
        raise
    except Exception as e:
        print(f"An error occurred with Ollama: {e}")
        raise



# download the listing image (store it in temporary storage)
def download_image(url: str) -> str:
    print(f"URL: {url}\n")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp.write(r.content)
    tmp.close()

    print(f"temp.name: {tmp.name}")

    return tmp.name


# json parsing
ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def extract_json(text: str):
    # Remove ANSI escape sequences
    clean = ANSI_ESCAPE.sub("", text)

    # Extract first JSON object
    match = re.search(r"\{[\s\S]*\}", clean)
    if not match:
        raise ValueError("No JSON object found")

    json_text = match.group()

    # Try strict parse first
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        # Last-resort fix: quote unquoted reason value
        fixed = re.sub(
            r'"reason"\s*:\s*([^"\n][^,\n}]*)',
            r'"reason": "\1"',
            json_text
        )
        return json.loads(fixed)


# endpoint (including prompt)
@app.post("/analyze")
def analyze(listing: Listing):

    prompt = f"""
You are an expert reseller who helps users decide if a marketplace listing is a good deal.

You are given:
- A product image
- A listing title
- An asking price

Your tasks are to:
1.  Assess the item's condition, authenticity, and completeness from the IMAGE.
2.  Identify the product and its market from the TITLE.
3.  Determine a fair resell value based on your assessment.
4.  Calculate a recommended **offer price** for the user to buy the item. This offer should be lower than the asking price to maximize the user's potential profit.

Listing title: {listing.title}
Asking price: ${listing.price}

Rules:
- The "offer" price must be less than or equal to the asking price.
- Be conservative in your assessment if the image is unclear.
- Your output must be ONLY a single, valid JSON object.
- All strings in the JSON must be enclosed in double quotes.

Return JSON in this exact format:
{{
  "score": 0-100,
  "offer": number,
  "resell": number,
  "reason": "string"
}}
    """

    # downloads the image
    # calls ollama with the injected prompt
    # extracts the json
    # returns the data to be displayed

    image_path = None

    try:
        if listing.image:
            image_path = download_image(listing.image)
        else:
            print(f"NO IMAGE PATH")

        raw = call_ollama(prompt, image_path)
        print("getting here (analyze)")
        data = extract_json(raw)
        return data

    except Exception:
        return {
            "score": 50,
            "offer": listing.price,
            "resell": listing.price,
            "reason": "Unable to confidently assess image or listing"
        }
