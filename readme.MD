# Job Salary Scraper and Analyzer

## Overview

This Python program scrapes job listings from Indeed based on a user-defined job search query and location(s). It collects and analyzes salary information from job postings and saves all job data into a JSON file. The program handles both yearly and hourly salaries, converting hourly wages to yearly estimates based on the job's schedule (full-time or part-time).

### Key Features

- **Job Scraping:** The program scrapes job listings from Indeed using BeautifulSoup and saves job data (title, company, location, salary, schedule, etc.) to a JSON file.
- **Salary Analysis:** It calculates the average, minimum, and maximum salary for each location, while converting hourly rates to annual salaries when appropriate.
- **Hourly Salary Conversion:** For jobs listed with an hourly wage, the program multiplies the hourly rate by an estimated number of hours worked per year (2,080 hours for full-time, 1,040 hours for part-time). Jobs without a specified schedule are excluded from the salary analysis.
- **JSON Export:** All scraped job data is saved to a JSON file named `all_jobs.json`.

---

## Installation

### Requirements

- Python 3.x
- Required Python packages:
  - `requests`
  - `beautifulsoup4`
  - `re` (regex for handling salary data)
  - `time`
  - `json`


## How to Use

### 1. Clone or Download the Repository

Clone the repository to your local machine or download the Python script.

### 2. Run the Script

1. Open a terminal or command prompt.
2. Navigate to the directory containing the Python script.
3. Run the script

### 3. Input Search Criteria

Once you run the script, it will prompt you for a job query and a list of locations:

- **Job Query:** Enter the job title or keywords you want to search for (e.g., "Software Engineer").
- **Locations:** Enter multiple locations separated by commas (e.g., "New York, San Francisco, Austin").

The script will then scrape job listings from Indeed for each location, analyze salary data, and save the results to a JSON file.

### 4. JSON Output

The script saves all job data into a JSON file named `all_jobs.json`. This file will include information about each job, including:

- Job Title
- Company Name
- Location
- Salary (or N/A if no salary info is provided)
- Job Type (e.g., Full-time, Part-time)
- Schedule (e.g., Day shift)

### 5. Salary Analysis

The script also prints out a detailed salary analysis for each location, showing:

- Average Salary
- Highest Salary
- Lowest Salary
- Total Salaries Analyzed

If no salary data is available for a location, the script will notify you.

---

## Example Usage

Here’s how the program would run:

```
$ python job_salary_scraper.py
Enter your search query: Data Scientist
Enter multiple locations separated by commas: New York, San Francisco, Austin

Scraping page 1 for location: New York
Scraping page 2 for location: New York
...
Scraping page 1 for location: San Francisco
...

All jobs have been saved to 'all_jobs.json'.

--- Salary Analysis Across Locations ---

Location: New York
Average Salary: $105,000.00
Highest Salary: $150,000.00
Lowest Salary: $80,000.00
Total Salaries Analyzed: 12

Location: San Francisco
Average Salary: $115,000.00
Highest Salary: $170,000.00
Lowest Salary: $90,000.00
Total Salaries Analyzed: 10

Location: Austin
No salary data available.
```

---

## Customization

You can customize the following aspects of the program:

1. **Number of Pages Scraped:** By default, the script scrapes 3 pages per location. You can change the `pages` parameter in the `compare_salaries()` function to adjust this.
2. **Handling More Job Data:** The script currently processes job title, company, location, salary, job type, and schedule. You can extend it to capture other details by modifying the `extract_job_data()` function.




