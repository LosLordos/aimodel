import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

class HockeyCrawler:
    def __init__(self):
        self.base_url = "https://www.hokej.cz/tipsport-extraliga/zapasy"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.data = []

    def scrape_season(self, season_id):
       
        print(f"Scraping season {season_id}...")
       
        url = f"{self.base_url}?season={season_id}"
        
        try:
           
            pass 
        except Exception as e:
            print(f"Error scraping season {season_id}: {e}")

    def save_data(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        
        df = pd.DataFrame(self.data)
        df.to_csv('data/matches_raw.csv', index=False)
        print(f"Saved {len(df)} matches to data/matches.csv")

if __name__ == "__main__":
    crawler = HockeyCrawler()
    
   
    target_seasons = [2023, 2024, 2025]
    
    print(f"Starting crawler for years: {target_seasons}")
    
    for season in target_seasons:
        crawler.scrape_season(season)
       
        time.sleep(1)
    
    crawler.save_data()
    print("Crawling process finished for specified years.")
