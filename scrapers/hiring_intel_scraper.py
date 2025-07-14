import os
import uuid
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from utils.supabase_client import supabase
from utils.ai_keywords import AI_KEYWORDS, is_ai_job

# === Load Company List from your actual CSV ===
csv_path = os.path.join(os.path.dirname(__file__), "../Competitor Master List (4).csv")
df = pd.read_csv(csv_path)

# Debug: Show the columns of the CSV
print("📑 CSV Columns:", df.columns)

# Make sure 'Title' exists in your CSV
if 'Title' not in df.columns:
    raise ValueError("❌ The CSV does not contain a 'Title' column. Please check the file.")

companies = df['Title'].dropna().unique().tolist()

# Debug: Print how many companies were loaded
print(f"📄 Loaded {len(companies)} companies from CSV")
print("🔍 Sample companies:", companies[:3])

# === Scrape Indeed for jobs ===
def scrape_indeed(company):
    print(f"🔎 Searching Indeed for: {company}")
    query = company.replace(" ", "+")
    url = f"https://www.indeed.com/jobs?q={query}&l=&sort=date"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []

    for card in soup.select(".result")[:5]:  # Top 5 jobs
        title_tag = card.select_one("h2.jobTitle span")
        location_tag = card.select_one(".companyLocation")
        link_tag = card.select_one("a")

        job_title = title_tag.text if title_tag else "N/A"
        location = location_tag.text if location_tag else "N/A"
        job_url = f"https://www.indeed.com{link_tag['href']}" if link_tag and 'href' in link_tag.attrs else "N/A"

        jobs.append({
            "id": str(uuid.uuid4()),
            "company_name": company,
            "job_title": job_title,
            "location": location,
            "post_date": datetime.now().date().isoformat(),
            "job_url": job_url,
            "is_ai_related": is_ai_job(job_title),
            "source": "Indeed",
            "created_at": datetime.now().isoformat()
        })

    return jobs

# === Upload to Supabase ===
def insert_jobs(jobs):
    for job in jobs:
        try:
            supabase.table("Hiring Intel").insert(job).execute()
            print(f"✅ Inserted: {job['job_title']} @ {job['company_name']}")
        except Exception as e:
            print(f"❌ Error inserting job: {e}")

# === Main Logic ===
if __name__ == "__main__":
    print("🚀 Starting Hiring Intel Scraper...\n")

    for company in companies:
        print(f"\n🔍 Scraping: {company}")
        try:
            results = scrape_indeed(company)
            print(f"📦 Found {len(results)} job(s)")
            insert_jobs(results)
        except Exception as e:
            print(f"❌ Error scraping {company}: {e}")
