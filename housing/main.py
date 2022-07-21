import time
from functions import download_data, merge_files
from performance import performance
from elements import MarketType, CITIES


if __name__ == '__main__':
    
    start = time.perf_counter()
    
    for city in CITIES[:3]:
        download_data(file_name=f"d_{city}.csv", 
                      search_criteria=[MarketType.SECONDARY, city, 24], 
                      number_of_pages=1) 

    end = time.perf_counter()
    
    main_file_name = "ALL_DATA"
    merge_files(file_format="d", file_identicators=CITIES[0:3], name=main_file_name)
    
    stats = performance(start, end, file_name=f"{main_file_name}.csv")
    print(stats)