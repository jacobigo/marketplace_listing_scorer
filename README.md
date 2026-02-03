# Facebook Marketplace AI Chrome Extension
## For analyzing listings, generating:
- ### an offer price
- ### potential resell value
- ### explanation for prices generated

## 
It's hard to assess what accurate prices are for different items on marketplace apps, and also how to make the best offer, as well as the best potential resell price.

This tool provides an easy way to analyze listings with local AI using a Chrome Extension, all while not having to navigate away from the app site.
##

## Usage:

### Frontend: Upload extension
- Navigate to ```chrome://extensions/```
- Turn on Developer Mode
- Locate the ```Load Unpacked``` button and upload the "Frontend" folder only

### Backend: Running the Python Server
- Find the ```server.py``` file
- Run it in your terminal: ```python -m uvicorn server:app --host 127.0.0.1 --port 8000```
    - Look at debug log in the terminal

## Tech Stack:
- ### Languages:
    Python, JavaScript
- ### Libraries (that need to be installed):
    - FastAPI
    - Requests
    - Pydantic
- ### Local AI:
  ####  Use Ollama and the model "llava-phi3"

