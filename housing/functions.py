from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag
import requests
from elements import CssStyle, SearchCriteria
from csv import writer
from tqdm import tqdm
import pandas as pd

### defining css properties ### 
"""otodom.pl website changes frequently. This means the structure of html is modified, 
and therefore its necessary to change CSS element descriptions. Defining these elements at the beginnig
allows quicker adjustments"""

LISTING = CssStyle("li", "css-p74l73 es62z2j17")
TITLE = CssStyle("div", "css-jeloly es62z2j12")
PRICE = CssStyle("span", "css-rmqm02 eclomwz0")
LOCATION = CssStyle("span", "css-17o293g es62z2j9")
GRID = CssStyle("div", "css-1qzszy5 estckra8")


### webscrapper functions ###
def get_all_page_listings(url: str) -> ResultSet:
    """Function scrapes data from otodom.pl and gathers html code containing
    list of offers on given result page"""
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    listings = soup.find_all(LISTING.element, class_=LISTING.class_)
    return listings


def extract_main_info(list_element: Tag) -> dict:
    """Function extracts main info from a list element 
    (that is a part of all listings on given page). Returning dict with title and price"""
    
    title = list_element.find(TITLE.element, class_=TITLE.class_).text
    price = list_element.find(PRICE.element, class_=PRICE.class_).text
    main_info = {"Tytuł": title, "Cena": price}
    return main_info


def extract_location_info(list_element: Tag) -> dict:
    """Functions finds listings's location. Location elements such as 
    city, district and street are separated by coma. Location_info function
    extracts each element and stores the values in dictionary"""
    
    location = list_element.find(LOCATION.element, class_=LOCATION.class_).text
    location_split = location.split(",")
    
    # try-except structere is required becouse 
    # locations don't neccesarily have to contain all described elemnts
    try: city = location_split[0]
    except IndexError: city = "NA"
    
    try: district = location_split[1].strip()
    except IndexError: district = "NA"

    try: street = location_split[2].strip()
    except IndexError: street = "NA"
    
    location_info = {"Miasto": city, "Dzielnica": district, "Ulica": street}
    return location_info


def get_offer_url(list_element: Tag) -> str:
    """Function extracts the link form particular listing, allowing the programme 
    to acess additional info. """
    
    offer_link = list_element.find('a', href=True)['href'] 
    offer_url = f"https://www.otodom.pl{offer_link}"
    return offer_url


def generate_offer_id(offer_url: str) -> str:
    """Function finds offer id, which is contained in the last link
    seven characters of an offer url"""
    return {"ID": offer_url[-7:]}


def get_offer_page_content(offer_url: str) -> BeautifulSoup:
    """Function acesses html code of specific offer page"""
    offer_page = requests.get(offer_url)
    offer_soup = BeautifulSoup(offer_page.content, 'html.parser')
    return offer_soup


def extract_detailed_info(offer_soup: ResultSet) -> dict:
    """Function extracts data form grid and table layout on specific offer page.
    Then cateory and values are appended to appropriate lists. The last step is matching
    category - value pairs in a dictionary format"""
    
    grid = offer_soup.find_all(GRID.element, class_=GRID.class_)
    
    categories = [item.text for index, item in enumerate(grid) if index % 2 == 0]
    values = [item.text for index, item in enumerate(grid) if index % 2 != 0]

    offer_data = {i:j for i, j in zip(categories, values)}
    return offer_data
    
    
def gather_offer_data(main_info: dict, location_info: dict, detailed_info: dict, id: dict) -> list: 
    """Function is responsible for gathering all the data. Try-except structure is required 
    to ensure there are no errors when information about specific category is not provided on the offer page. 
    In case there is no relevant data from some category, "NA" values are inputted. 
    During the last step, function summarizes the data in a list (later it is simple to add 
    individial lists as separate records to csv file)"""
    
    all_offer_data = main_info | location_info | detailed_info | id

    selected_columns = ("ID", "Tytuł", "Cena", "Miasto", "Dzielnica", "Ulica", 
                        "Powierzchnia", "Liczba pokoi", "Czynsz", "Piętro", "Rok budowy",
                        "Balkon / ogród / taras", "Miejsce parkingowe", "Winda", "Wyposażenie",
                        "Informacje dodatkowe", "Typ ogłoszeniodawcy", "Rynek", "Forma własności")
    offer_data_list = []
    for key in selected_columns:
        try: 
            offer_data_list.append(all_offer_data[key])
        except KeyError: 
            offer_data_list.append("NA")
            
    return offer_data_list

def generate_url_list(criteria: SearchCriteria, pages: int) -> list:
    """Function creates a list of search url that match criteria. 
    Then the result (list) can be used as iterator in webscrapper."""
    
    url_list = [criteria.generate_url(i) for i in list(range(1, pages + 1))]
    return url_list    

def download_data(file_name: str, search_criteria: list, number_of_pages: str) -> None:
    """Functions is implementation-ready web scraper, combining all the assets described above. 
    Creates a csv file with downloaded offer data records, filtered by provided search_criteria.
    User can specify the number of result pages to scrape."""
    
    with open(file_name, 'w', encoding='utf8', newline='') as f:
        thewriter = writer(f)

        header = ["id", "title", "price", "city", "district", "street", 
                  "area", "rooms", "rent", "floor", "year", 
                  "balcony", "garage", "elevator", "furnishing", "extra_info",
                  "seller_type", "market", "ownership"]
        thewriter.writerow(header)
        
        print(f"\nFile: {file_name} has been created.\n")

        search = SearchCriteria(search_criteria[0], search_criteria[1], search_criteria[2])
        search_pages = generate_url_list(criteria=search, pages=number_of_pages)
        
        page_num = 1
        for page_url in search_pages:
            offer_list = get_all_page_listings(page_url)
            
            num_results = len(offer_list)
            print(f"Adding page {page_num} content >>>")
            page_num += 1
            
            pbar = tqdm(total=num_results)
            
            for offer in offer_list:
                main_info = extract_main_info(offer)
                location_info = extract_location_info(offer)

                # offer link + id 
                offer_url = get_offer_url(offer)
                offer_id = generate_offer_id(offer_url)

                # accessing offer data
                offer_soup = get_offer_page_content(offer_url)
                detailed_info = extract_detailed_info(offer_soup)

                # all info
                all_info = gather_offer_data(main_info, location_info, detailed_info, offer_id)

                # add data to csv
                thewriter.writerow(all_info)
                
                pbar.update()
                
            pbar.close()
            
def merge_files(file_format: str, file_identicators: list[str], name: str) -> None:
    """Merges all the separate files. Creates new csv file containing all the data."""
    try: 
        dataframes = [pd.read_csv(f"{file_format}_{i}.csv") for i in file_identicators]
        all_data = pd.concat(dataframes).reset_index()
        all_data.to_csv(f"{name}.csv")
    except FileNotFoundError:
        print("Wrong file_format or file_identificators have been provided")    