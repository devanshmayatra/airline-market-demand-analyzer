import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
from groq import Groq
from serpapi import GoogleSearch
from fastapi.staticfiles import StaticFiles
import re

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AIRLINE_SEARCH_URLS = {
    "United": "https://www.united.com",
    "Delta": "https://www.delta.com",
    "Air France": "https://www.airfrance.us",
    "Etihad": "https://www.etihad.com",
    "Virgin Atlantic": "https://www.virginatlantic.com",
    "Lufthansa": "https://www.lufthansa.com",
}

# Constants
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# WEB SCRAPER
def scrape_flight_data(origin: str, destination: str, date:str):
    try:
        params = {
            "api_key": SERPAPI_API_KEY,
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "type": "2",
            "currency": "USD",
            "hl": "en"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
                
        if 'error' in results:
            print(f"!!! SERPAPI ERROR: {results['error']} !!!")
        
        if 'best_flights' not in results or not results['best_flights']:
            return {"offers": [], "trends": []}

        processed_offers = []
        for flight_offer in results.get('best_flights', []):
            if 'flights' in flight_offer and flight_offer['flights']:
                main_flight = flight_offer['flights'][0]
                processed_offers.append({
                    "airline": main_flight.get('airline', 'N/A'),
                    "price": float(flight_offer.get('price', 0)),
                    "departure": f"{main_flight.get('departure_airport', {}).get('time', 'N/A')}",
                    "arrival": f"{main_flight.get('arrival_airport', {}).get('time', 'N/A')}",
                    "travel_class":main_flight.get('travel_class','N/A')
                })
        return {"offers": processed_offers, "trends": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred with the Web Scraper: {str(e)}")

# API Endpoints
@app.get("/api/status")
def read_root():
    return {"message": "Airline Market Analyzer API is running."}

@app.get("/api/analyze-route")
def analyze_route(origin: str, destination: str, source: str = 'api', date: str = None):
    print(f"Received request for {origin}->{destination} using source: {source} date: {date}")

    return scrape_flight_data(origin, destination, date)


@app.post("/api/generate-insights")
def generate_insights(data: dict):
    simplified_data = {
        "origin": data.get("origin"),
        "destination": data.get("destination"),
        "current_offers": data.get("offers", []),
        "price_trends_sample": data.get("trends", [])[:10]
    }
    
    prompt = f"""
    You are an expert airline market analyst. Analyze the following flight data and market trends to deliver a concise, actionable summary of current flight offers.

    Flight Data:
    {json.dumps(simplified_data, indent=2)}

    Guidelines:
    - Output only bullet points.
    - Highlight the cheapest option, best departure times, and price competitiveness.
    - Keep recommendations clear, direct, and actionable for a traveler.
    """
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], 
            model="groq/compound"
        )
        
        return {"insights": chat_completion.choices[0].message.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")