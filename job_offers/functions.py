from dataclasses import dataclass
from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag
from elements import SearchCriteria
import requests
from csv import writer
from numpy import nan
from tqdm import tqdm


def get_all_page_listings(url: str) -> list:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    listings = soup.find_all('a', href=True)
    
    unedited_links = [j['href'] for i, j in enumerate(listings) if ("job" in j['href']) and (i > 7)]
    links = [f"https://nofluffjobs.com{link}" for link in unedited_links]
    return links

def get_offer_page_content(url: str) -> BeautifulSoup:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    return soup

def extract_position(page_content: BeautifulSoup) -> dict:
    
    try:
        position = page_content.find("h1", class_="font-weight-bold bigger")
        position_name = position.text.strip()
    except AttributeError:
        try:
            position = page_content.find("h1", class_="font-weight-bold")
            position_name = position.text.strip()
        except AttributeError:
            position_name = "unknown"
            
    return {"position": position_name}
   
def extract_company(page_content: BeautifulSoup) -> dict:
    try: 
        company = page_content.find("a", class_="inline-info d-flex align-items-center text-primary")
        company_name = company.text.strip()
    except AttributeError:
        try:
            company = page_content.find("a", class_="inline-info d-flex align-items-center")
            company_name = company.text.strip()
        except AttributeError:
            company_name = "Unknown company"
    
    return {"company": company_name}

def extract_salary(page_content: BeautifulSoup) -> dict:
    salary = page_content.find_all("h4", class_="mb-0")
    salary_info = [i.text.strip().replace(" ", "").replace(u"\xa0", u"") for i in salary]
    
    return {"salary": salary_info}
     
def extract_requirements(page_content: BeautifulSoup) -> dict:
    requirements = page_content.find_all("common-posting-item-tag")
    types = page_content.find_all("common-posting-requirements")
    
    all_reqs= [i.text.strip() for i in requirements]
    reqs_by_type = [i.text for i in types]
    
    main = [i for i in all_reqs if i in reqs_by_type[0]]
    
    length = len(reqs_by_type)
    if length == 2:
        secondary = [i for i in all_reqs if i in reqs_by_type[1]]
    else:
        secondary = ["No secondary requirements"]
    
    return {"requirements_main": main, "requirements_secondary": secondary}

def extract_description(page_content: BeautifulSoup) -> dict:
    description = page_content.find("nfj-read-more", class_="font-weight-normal")
    try: 
        text = description.text
    except AttributeError:
        text = "No description"
        
    return {"description": text}
    
def extract_tasks(page_content: BeautifulSoup) -> dict:
    tasks_top5 = page_content.find_all("p", class_="d-flex align-items-center mb-0 mb-3")
    tasks_last = page_content.find("p", class_="d-flex align-items-center mb-0")
    
    tasks = [i.text.strip() for i in tasks_top5]
    
    try:
        last_item = tasks_last.text.strip()
        tasks.append(last_item)
    except AttributeError:
        pass
    
    return {"tasks": tasks}

def extract_specs(page_content: BeautifulSoup) -> dict:
    specs = page_content.find_all("p", class_="d-inline-flex align-items-center font-size-14 detail mr-10 mb-10")
    spec_list = [i.text for i in specs]
    
    return {"posting_specs": spec_list}
    
def extract_methodology(page_content: BeautifulSoup) -> dict:
    methodologies = page_content.find_all("div", class_="d-flex position-relative font-size-14 mb-10")
    methodologies_last = page_content.find("div", class_="d-flex position-relative font-size-14")
    
    methodologies_list = [i.text.strip() for i in methodologies]
    try:
        methodologies_list.append(methodologies_last.text.strip())
    except AttributeError:
        pass
    
    return {"methodology": methodologies_list}
    
def extract_benefits(page_content: BeautifulSoup) -> dict:
    benefits = page_content.find_all("div", class_="col-sm-6 perk mt-10")
    benefits_list = [i.text.strip() for i in benefits]
    
    return {"benefits": benefits_list}

def extract_equipment(page_content: BeautifulSoup) -> dict:
    equipment = page_content.find_all("p", class_="mobile-text mb-0 mt-1 font-size-11 text-center")
    equipment_list = [i.text.strip() for i in equipment]
    
    return {"equipment": equipment_list}

def gather_all_info(position: dict, company: dict, salary: dict, requirements: dict,
                    description: dict, tasks: dict, specs: dict, methodology: dict, 
                    benefits: dict, equipment: dict) -> list: 
    all_data = position | company | salary | requirements | description | tasks | specs | methodology | \
        benefits | equipment
    
    offer_data_list = []
    for key in all_data.keys():
        try: 
            offer_data_list.append(all_data[key])
        except KeyError: 
            offer_data_list.append(nan)
    return offer_data_list

def generate_search_url_list(criteria: SearchCriteria, pages: int) -> list: 
    url_list = (criteria.generate_url(i) for i in list(range(1, pages+1)))
    return url_list
 
def download_data(file_name: str, search_criteria: str, number_of_pages: str) -> None:

    with open(file_name, 'w', encoding='utf8', newline='') as f:
        thewriter = writer(f)

        header = ['position', 'company', 'salary', 'requirements_main', 
                  'requirements_secondary',
                  'description', 'tasks', 'specs', 'methodology', 
                  'benefits', 'equipment']
        thewriter.writerow(header)
        
        print(f"\nFile: {file_name} has been created.\n")

        search = SearchCriteria(search_criteria)
        search_pages = generate_search_url_list(criteria=search, pages=number_of_pages)
        
        page_num = 1
        for page_url in search_pages:
            offer_url_list = get_all_page_listings(page_url)
            
            num_results = len(offer_url_list)
            print(f"Adding page {page_num} content >>>")
            page_num += 1
            
            pbar = tqdm(total=num_results)
            
            for offer in offer_url_list:
                soup = get_offer_page_content(offer)
                
                
                position = extract_position(soup)
                company = extract_company(soup)
                salary = extract_salary(soup)
                
                requirements = extract_requirements(soup)
                description = extract_description(soup)
                tasks = extract_tasks(soup)
                
                specs = extract_specs(soup)
                methodology = extract_methodology(soup)
                benefits = extract_benefits(soup)
                equipment = extract_equipment(soup)
                
                all_offer_data = gather_all_info(position, company, salary, requirements,
                                                 description, tasks, specs, methodology, 
                                                 benefits, equipment)
                
                thewriter.writerow(all_offer_data)
                
                pbar.update()
  
            pbar.close()