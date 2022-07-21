from dataclasses import dataclass
from email import generator
from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag
import requests
from csv import writer
from numpy import nan
from tqdm import tqdm


@dataclass(slots=True)
class SearchCriteria:
    brand: str
    
    def generate_url(self, page_number=1) -> str:
        url = f"https://www.otomoto.pl/osobowe/{self.brand}?page={page_number}"
        return url   
    
    
def get_all_page_listings(url: SearchCriteria) -> ResultSet:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    listings = soup.find_all("div", class_="ooa-1nvnpye e1b25f6f5")
    return listings


def extract_offer_url(list_item: Tag) -> str:
    offer_link = list_item.find('a', href=True)['href'] 
    return offer_link


def offer_page_content(url: str) -> BeautifulSoup:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    return soup


def extract_table_info(offer_soup: BeautifulSoup) -> dict:
    listings = offer_soup.find_all("li", class_="offer-params__item")
    
    categories = [i.find("span", class_="offer-params__label").text for i in listings]
    values = [i.find("div", class_="offer-params__value").text.strip() for i in listings]
    
    offer_dictionary = {i:j for i, j in zip(categories, values)}
    return offer_dictionary


def extract_price(offer_soup: BeautifulSoup) -> dict:
    price = offer_soup.find("span", class_="offer-price__number")
    price_cleaned = price.text.strip().replace(" ", "")
    return {"Cena": price_cleaned}


def gather_offer_data(price: dict, offer_details:dict) -> list:
    all_offer_data = {**price, **offer_details}
    
    selected_columns = ['Cena', 'Marka pojazdu', 'Model pojazdu', 'Wersja', 
               'Rok produkcji', 'Przebieg', 'Rodzaj paliwa', 'Moc', 
               'Skrzynia biegów', 'Napęd', 'Spalanie W Mieście', 'Stan']
    
    offer_data_list = []
    for key in selected_columns:
        try: 
            offer_data_list.append(all_offer_data[key])
        except KeyError: 
            offer_data_list.append(nan)
    return offer_data_list


def generate_url_list(criteria: SearchCriteria, pages: int) -> generator: 
    url_list = (criteria.generate_url(i) for i in list(range(1, pages+1)))
    return url_list


def download_data(file_name: str, search_criteria: str, number_of_pages: str) -> None:

    with open(file_name, 'w', encoding='utf8', newline='') as f:
        thewriter = writer(f)

        header = ['Cena', 'Marka pojazdu', 'Model pojazdu', 'Wersja', 
                  'Rok produkcji', 'Przebieg', 'Rodzaj paliwa', 'Moc', 
                  'Skrzynia biegów', 'Napęd', 'Spalanie W Mieście', 'Stan']
        thewriter.writerow(header)
        
        print(f"\nFile: {file_name} has been created.\n")

        search = SearchCriteria(search_criteria)
        search_pages = generate_url_list(criteria=search, pages=number_of_pages)
        
        page_num = 1
        for page_url in search_pages:
            offer_list = get_all_page_listings(page_url)
            
            num_results = len(offer_list)
            print(f"Adding page {page_num} content >>>")
            page_num += 1
            
            pbar = tqdm(total=num_results)
            
            for offer in offer_list:
                offer_link = extract_offer_url(offer)

                offer_soup = offer_page_content(offer_link)
                offer_details = extract_table_info(offer_soup)
                price = extract_price(offer_soup)

                all_offer_data = gather_offer_data(price, offer_details)

                thewriter.writerow(all_offer_data)
                
                pbar.update()
                
            pbar.close()