This repo contains one script "find_scrape.py" that collects Name and About data from the website https://intro.co/marketplace. 
It also contains 5 CSV files that has experts info corresponding to five catogories that the website provides: Top experts, Home, Wellness, Career & Business, and Style & Beauty.
Note that people in the category of top experts can also be shown in other categories.
Profiles 0 to 2 should have no duplicates, while I don't want to re-scrape the whole wesite again after handling HTTPs timeout error, profiles 3 and 4 are scraped in a different section than 0-2. Hence they might have dupicates with profile_0.csv.
