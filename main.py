import requests
from bs4 import BeautifulSoup
import time
import re
import json

# mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Function to extract job data from 'resultContent' td elements
def extract_jobs_from_page(soup):
    job_listings = []

    # Find all <td> elements with class 'resultContent'
    job_cards = soup.find_all('td', class_='resultContent')

    for card in job_cards:
        job_data = extract_job_data(card)
        job_listings.append(job_data)

    return job_listings

# Function to extract and clean relevant job data
def extract_job_data(td):
    job_data = {}

    # Extract job title
    job_title = td.find('h2', class_='jobTitle')
    job_data['title'] = job_title.get_text().strip() if job_title else 'N/A'

    # Extract company name
    company_name = td.find('span', class_='css-63koeb')
    job_data['company'] = company_name.get_text().strip() if company_name else 'N/A'

    # Extract location
    location = td.find('div', class_='css-1p0sjhy')
    job_data['location'] = location.get_text().strip() if location else 'N/A'

    # Extract salary
    salary = td.find('div', class_='salary-snippet-container')
    job_data['salary'] = salary.get_text().strip() if salary else 'N/A'

    # Extract job type or other metadata
    metadata = td.find_all('div', class_='css-1cvvo1b')
    job_data['job_type'] = metadata[1].get_text().strip() if len(metadata) > 1 else 'N/A'
    job_data['schedule'] = metadata[2].get_text().strip() if len(metadata) > 2 else 'N/A'

    return job_data

# Function to clean and convert salary data
def parse_salary(salary_str):
    # Look for salary in the format of "$50,000 - $60,000 a year" or "From $70,000 a year"
    if salary_str:
        salary_range = re.findall(r'\$[\d,]+', salary_str)
        if len(salary_range) == 2:  # Salary range
            salary_min = int(salary_range[0].replace('$', '').replace(',', ''))
            salary_max = int(salary_range[1].replace('$', '').replace(',', ''))
            return (salary_min + salary_max) // 2  # Average of min and max
        elif len(salary_range) == 1:  # Single salary value like "From $70,000 a year"
            return int(salary_range[0].replace('$', '').replace(',', ''))
    return None

# Function to scrape multiple pages and perform salary analysis
def scrape_indeed_jobs(query, location, pages=5):
    base_url = "https://www.indeed.com/jobs"
    all_jobs = []
    salary_values = []

    for page in range(0, pages):
        # Construct the full URL for the current page
        params = {
            'q': query,
            'l': location,
            'start': page * 10  # Indeed paginates by 10 results per page
        }
        print(f"Scraping page {page + 1}")

        # Send a GET request to the page with headers
        response = requests.get(base_url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract jobs from the current page
            jobs = extract_jobs_from_page(soup)

            # Add jobs to the overall job list
            all_jobs.extend(jobs)

            # Extract and clean salary data
            for job in jobs:
                salary_value = parse_salary(job['salary'])
                if salary_value:
                    salary_values.append(salary_value)

            # Pause between requests to avoid overwhelming the server
            time.sleep(2)
        else:
            print(f"Failed to retrieve page {page + 1}. Status code: {response.status_code}")

    # Salary Analysis
    if salary_values:
        avg_salary = sum(salary_values) / len(salary_values)
        max_salary = max(salary_values)
        min_salary = min(salary_values)

        print(f"\n--- Salary Analysis ---")
        print(f"Average Salary: ${avg_salary:,.2f}")
        print(f"Highest Salary: ${max_salary:,.2f}")
        print(f"Lowest Salary: ${min_salary:,.2f}")
        print(f"Total Salaries Analyzed: {len(salary_values)}")
    else:
        print("\nNo salary data available for analysis.")

    return all_jobs

# Function to save the jobs to a JSON file
def save_jobs_to_json(jobs, filename="jobs_data.json"):
    with open(filename, 'w') as json_file:
        json.dump(jobs, json_file, indent=4)

# Specify job query and location
query = input("Enter your search query: ")
location = input("Enter your location: ")

# Scrape job data from the first 3 pages
scraped_jobs = scrape_indeed_jobs(query, location, pages=3)

# Save the scraped jobs to a JSON file
save_jobs_to_json(scraped_jobs, filename="indeed_jobs.json")

print(f"\nJob data saved to 'indeed_jobs.json'")
