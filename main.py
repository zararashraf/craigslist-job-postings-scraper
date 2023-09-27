from datetime import datetime
from config import location_to_batch, category_to_abbreviation
import csv
import requests

def fetch_job_postings(location, category, batch):
    base_url = "https://sapi.craigslist.org/web/v8/postings/search/full"

    # Get the batch value and category abbreviation from the mappings
    # Default to New York if location not found
    batch = location_to_batch.get(location, "3-0-360-0-0")  
    category_abbreviation = category_to_abbreviation.get(category, "etc") 

    params = {
        'batch': batch,
        'cc': 'US',
        'lang': 'en',
        'searchPath': category_abbreviation,
    }

    headers = {
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'Referer': f'https://{location}.craigslist.org/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'cl_b=4|c1f3482a2bf4a1b367abd45e5c44d10532e2d9df|16950580739tgOc'
    }

    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        data = None

    job_postings = []

    if data:
        for item in data["data"]["items"]:
            job_title = None
            commission = None
            for element in item:
                if isinstance(element, str):
                    job_title = element
                elif isinstance(element, list) and len(element) > 0 and element[0] == 7:
                    commission = element[1]
            if job_title and commission:
                job_postings.append((job_title, commission))
        
        return job_postings
                
    else:
        print("No data available.")

if __name__ == "__main__":
    location = "philadelphia"
    category = "software/qa/dba/etc" # Please refer to the config.py file for another category
    batch = "17-0-360-0-0" # This is the batch number for the location, more important than the location (variable) to fetch jobs from different location. You can get batches from craigslist and put them in the config.py file.
    
    job_postings = fetch_job_postings(location, category, batch)

    if job_postings:
       
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        category = category.replace("/", "&")
        csv_filename = f"{location}_{category}_openings_{current_datetime}.csv"

        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow(["Job Title", "Commission"])
            for job in job_postings:
                writer.writerow([job[0], job[1]])
        
        print(f"Job postings have been saved to {csv_filename}")
    else:
        print("No data available.")
