import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import json
from groq import Groq
from serpapi import GoogleSearch

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_SECRET_KEY = os.getenv("AMADEUS_SECRET_KEY")
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_API_BASE_URL = "https://test.api.amadeus.com/v2"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Get Tokens
def get_amadeus_token():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_SECRET_KEY,
    }
    try:
        response = requests.post(AMADEUS_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        error_detail = f"Failed to authenticate with Amadeus API. Response: {e.response.text if e.response else 'No response'}"
        raise HTTPException(status_code=500, detail=error_detail)

# Get Data Fom Amadeus API
def get_amadeus_data(origin: str, destination: str):
    try:
        token = get_amadeus_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        offers_url = f"{AMADEUS_API_BASE_URL}/shopping/flight-offers"
        offers_params = {"originLocationCode": origin, "destinationLocationCode": destination, "departureDate": "2025-11-20", "adults": 1, "max": 15, "currencyCode": "INR"}
        offers_response = requests.get(offers_url, headers=headers, params=offers_params)
        offers_response.raise_for_status()
        offers_data = offers_response.json()

        cheapest_data = {}
        try:
            cheapest_date_url = f"https://test.api.amadeus.com/v1/shopping/flight-cheapest-date-search"
            cheapest_params = {"origin": origin, "destination": destination, "currencyCode": "INR"}
            cheapest_response = requests.get(cheapest_date_url, headers=headers, params=cheapest_params)
            cheapest_response.raise_for_status()
            cheapest_data = cheapest_response.json()
        except requests.exceptions.HTTPError as e:
            print(f"!!! WARNING: Amadeus Cheapest Date Search API failed. Proceeding without trend data. !!!")

        processed_offers = []
        if 'data' in offers_data and offers_data['data']:
            dictionaries = offers_data.get('dictionaries', {})
            for offer in offers_data['data']:
                carrier_code = offer['itineraries'][0]['segments'][0]['carrierCode']
                processed_offers.append({"airline": dictionaries.get('carriers', {}).get(carrier_code, carrier_code), "price": float(offer['price']['total']), "departure": offer['itineraries'][0]['segments'][0]['departure']['at'], "arrival": offer['itineraries'][0]['segments'][-1]['arrival']['at']})
        
        return {"offers": processed_offers, "trends": cheapest_data.get('data', [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred with the Amadeus API: {str(e)}")

# WEB SCRAPER
def scrape_flight_data(origin: str, destination: str):
    try:
        params = {
            "api_key": SERPAPI_API_KEY,
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": "2025-09-16",
            "type": "2",
            "currency": "AUD",
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
                    "arrival": f"{main_flight.get('arrival_airport', {}).get('time', 'N/A')}"
                })
        
        return {"offers": processed_offers, "trends": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred with the Web Scraper: {str(e)}")

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Airline Market Analyzer API is running."}

@app.get("/api/analyze-route")
def analyze_route(origin: str, destination: str, source: str = 'api'):
    print(f"Received request for {origin}->{destination} using source: {source}")
    if source == 'scraper':
        return scrape_flight_data(origin, destination)
    else:
        return get_amadeus_data(origin, destination)

@app.post("/api/generate-insights")
def generate_insights(data: dict):
    simplified_data = {"current_offers": data.get("offers", []), "price_trends_next_months": data.get("trends", [])}
    prompt = f"""
    You are a market analyst for a chain of youth hostels in Australia... (prompt unchanged)
    Data: {json.dumps(simplified_data)}
    Provide only the bullet-point summary. Be clear and actionable.
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
        return {"insights": chat_completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")