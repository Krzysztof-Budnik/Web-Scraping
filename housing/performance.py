from pandas import read_csv


def performance(start: float, end: float, file_name: str) -> str:
    execution_time = end - start
    num_records = len(read_csv(file_name))
    time_per_record = execution_time / num_records

    message = f"""\nTotal execution time is: {execution_time:.2f} sec ({execution_time/60:.2f} min or {execution_time/3600:.2f} h)
Data records downloaded: {num_records} 
Program downloaded data at speed: {time_per_record:.2f} sec per one record\n"""
    return message