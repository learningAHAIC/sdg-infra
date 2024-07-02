import re
from bs4 import BeautifulSoup as soup
import os
import requests
import csv
from tqdm import tqdm
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# TODO: edit global vars
target_url = "https://www.examplebank.org/projects"
hah = '?page='
max_page = 100 
folder = './bank_name'
outputfile = 'outputfile.csv'

projects = []
lock = threading.Lock()

class Project:
    def __init__(self, name, project_id='nan', country='nan', status='nan', project_type='nan', fund='nan', date='nan'):
        self.name = name  # Name of the project
        self.project_id = project_id  # Unique identifier for the project
        self.country = country  # Country where the project is located
        self.status = status  # Current status of the project (e.g., 'ongoing', 'completed')
        self.project_type = project_type  # Type of the project (e.g., 'infrastructure', 'research')
        self.fund = fund  # Funding amount for the project
        self.date = date # Date associated with the project (e.g., start date)

    def to_dict(self):
        return {
            'name': self.name,
            'project_id': self.project_id,
            'country': self.country,
            'status': self.status,
            'project_type': self.project_type,
            'fund': self.fund,
            'date': self.date,
        }

def read_projects(link):
    r = requests.get(link)
    page_soup = soup(r.content, "html.parser")
    links = [target_url + a['href'] for a in page_soup.find_all('a', href=True)]
    for k in links:
        p_r = requests.get(k)
        p_soup = soup(p_r.content, "html.parser").get_text()
        p_name = 'nan'
        # TODO: implement your own regex
        match = re.search(r'implement your own regex', p_soup)
        if match:
            p_name = match.group(0)
        # TODO: it might need more things than just a name
        
        # thread and lock
        with lock:
            projects.append(Project(p_name))
        
def projects_tocsv(csv_file):
    # Write the list of projects to a CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'project_id', 'country', 'status', 'project_type', 'fund', 'date'])
        writer.writeheader()
        for project in projects:
            writer.writerow(project.to_dict())

def main():
    # try to create a folder locally for the bank
    os.mkdir(folder)
        
    url_list = [target_url + hah + j for j in range(max_page)]
    
    progress_bar = tqdm(total=len(url_list))
    # Function to update the progress bar
    def update_progress(future):
        progress_bar.update()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(read_projects, link) for link in url_list]
        for future in futures:
            future.add_done_callback(update_progress)
        for future in as_completed(futures):
            pass
            
    progress_bar.close()
    
    projects_tocsv(outputfile)