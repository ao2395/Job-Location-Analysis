import requests
from bs4 import BeautifulSoup
import time
import json
import re

# Mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Constants for hourly salary conversion
FULL_TIME_HOURS_PER_YEAR = 40 * 52  # 40 hours/week * 52 weeks/year
PART_TIME_HOURS_PER_YEAR = 20 * 52  # 20 hours/week * 52 weeks/year

# Function to extract job data from 'resultContent' td elements
def extract_jobs_from_page(soup):
    job_listings = []
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
def parse_salary(salary_str, schedule):
    if salary_str:
        salary_range = re.findall(r'\$[\d,]+', salary_str)
        if "hour" in salary_str.lower():  # Handle hourly salaries
            if schedule:
                if "full" in schedule.lower():
                    avg_hours_per_year = FULL_TIME_HOURS_PER_YEAR
                elif "part" in schedule.lower():
                    avg_hours_per_year = PART_TIME_HOURS_PER_YEAR
                else:
                    return None  # Ignore if schedule is unclear or missing
            else:
                return None  # Ignore hourly salary if schedule is missing

            if len(salary_range) == 1:  # Single hourly rate
                hourly_rate = int(salary_range[0].replace('$', '').replace(',', ''))
                return hourly_rate * avg_hours_per_year
        elif len(salary_range) == 2:  # Salary range
            salary_min = int(salary_range[0].replace('$', '').replace(',', ''))
            salary_max = int(salary_range[1].replace('$', '').replace(',', ''))
            return (salary_min + salary_max) // 2  # Average of min and max
        elif len(salary_range) == 1:  # Single salary value like "From $70,000 a year"
            return int(salary_range[0].replace('$', '').replace(',', ''))
    return None

# Function to scrape Indeed jobs for a given query and location
def scrape_indeed_jobs(query, location, pages=5):
    base_url = "https://www.indeed.com/jobs"
    all_jobs = []
    salary_values = []

    for page in range(0, pages):
        params = {
            'q': query,
            'l': location,
            'start': page * 10  # Indeed paginates by 10 results per page
        }
        print(f"Scraping page {page + 1} for location: {location}")

        # Send a GET request to the page with headers
        response = requests.get(base_url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = extract_jobs_from_page(soup)
            all_jobs.extend(jobs)

            # Extract and clean salary data
            for job in jobs:
                salary_value = parse_salary(job['salary'], job['schedule'])
                if salary_value:
                    salary_values.append(salary_value)

            time.sleep(2)
        else:
            print(f"Failed to retrieve page {page + 1}. Status code: {response.status_code}")

    # Return both job listings and salary values
    return all_jobs, salary_values

# Function to compare salary data across locations and save the JSON file
def compare_salaries(query, locations, pages=5):
    all_jobs_collected = []
    salary_analysis = {}

    for location in locations:
        jobs, salaries = scrape_indeed_jobs(query, location, pages)
        all_jobs_collected.extend(jobs)  # Collect jobs from all locations

        if salaries:  # Perform salary analysis only if salaries are found
            avg_salary = sum(salaries) / len(salaries)
            max_salary = max(salaries)
            min_salary = min(salaries)
            salary_analysis[location] = {
                "average_salary": avg_salary,
                "max_salary": max_salary,
                "min_salary": min_salary,
                "total_salaries_analyzed": len(salaries)
            }
        else:
            salary_analysis[location] = "No salary data available"

    # Save all jobs to a JSON file
    save_jobs_to_json(all_jobs_collected, filename="all_jobs.json")

    # Print salary analysis
    print("\n--- Salary Analysis Across Locations ---")
    for location, analysis in salary_analysis.items():
        if isinstance(analysis, dict):
            print(f"\nLocation: {location}")
            print(f"Average Salary: ${analysis['average_salary']:,.2f}")
            print(f"Highest Salary: ${analysis['max_salary']:,.2f}")
            print(f"Lowest Salary: ${analysis['min_salary']:,.2f}")
            print(f"Total Salaries Analyzed: {analysis['total_salaries_analyzed']}")
        else:
            print(f"\nLocation: {location}")
            print("No salary data available.")

# Function to save jobs to a JSON file
def save_jobs_to_json(jobs, filename="jobs_data.json"):
    # Ensure all job entries are clean for JSON serialization
    cleaned_jobs = []
    for job in jobs:
        cleaned_job = {
            "title": job.get("title", "N/A"),
            "company": job.get("company", "N/A"),
            "location": job.get("location", "N/A"),
            "salary": job.get("salary", "N/A"),
            "job_type": job.get("job_type", "N/A"),
            "schedule": job.get("schedule", "N/A")
        }
        cleaned_jobs.append(cleaned_job)

    # Try saving the cleaned data to JSON
    try:
        with open(filename, 'w') as json_file:
            json.dump(cleaned_jobs, json_file, indent=4)
        print(f"Job data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

# Main script
query = input("Enter your search query: ")
locations = input("Enter multiple locations separated by commas: ").split(',')

# Compare salaries across multiple locations and save the jobs data to JSON
compare_salaries(query, [loc.strip() for loc in locations], pages=5)
