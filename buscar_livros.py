import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_BOOKS_KEY")
GOOGLE_LIVROS_URL = "https://www.googleapis.com/books/v1/volumes"

autores = []

if autores:
    for autor in autores:
        params = {
            "q": f'inauthor:"{autor}"',
            "printType": "books",
            "orderBy": "relevance",
            "maxResults": 40,
            "key": GOOGLE_API_KEY
        }

        response = requests.get(GOOGLE_LIVROS_URL, params=params)
        response.raise_for_status()

        data = response.json()

        with open(f"./autores/{autor.lower().replace(' ', '_')}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
