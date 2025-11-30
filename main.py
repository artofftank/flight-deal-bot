import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError
import pandas as pd

load_dotenv()

def find_deals():
    try:
        amadeus = Client(
            client_id=os.getenv('AMADEUS_API_KEY'), 
            client_secret=os.getenv('AMADEUS_API_SECRET')
            )
        offers = amadeus.shopping.flight_offers_search.get(
            originLocationCode='TIJ',
            destinationLocationCode='CUN',
            departureDate='2026-02-01',
            returnDate='2026-02-05',
            adults=1,
            currencyCode='USD',
            max=5
        )
        
        carrier_names = offers.result['dictionaries']['carriers']

        for offer in offers.data:
            code = offer['validatingAirlineCodes'][0]
            full_name = carrier_names.get(code, code)
            offer['airline_name'] = full_name
        print(f"Found {len(offers.data)} flight offers.")

        return offers.data
    
    except ResponseError as error:
        print(f"❌ Error: {error}")

    
def export_offers(offers_data, filename_base='flight_offers'):
    if not offers_data:
        print("No offers to export.")
        return
    
    df = pd.json_normalize(offers_data)

    export_folder = 'exports'
    os.makedirs(export_folder, exist_ok=True)

    csv_path = os.path.join(export_folder, f"{filename_base}.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ Exported offers to csv {csv_path}")


    json_path = os.path.join(export_folder, f"{filename_base}.json")
    df.to_json(json_path, orient='records', indent=4)
    print(f"✅ Exported offers to json {json_path}")

if __name__ == "__main__":
    flights = find_deals()

    if flights:
        export_offers(flights)