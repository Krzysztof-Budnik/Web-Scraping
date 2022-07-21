import time
from functions import download_data
from performance import performance


if __name__ == '__main__':
    
    start = time.perf_counter()

    download_data(file_name="TEST_DATA.csv", search_criteria="audi", number_of_pages=2) 

    end = time.perf_counter()

    stats = performance(start, end, file_name="TEST_DATA.csv")
    print(stats)