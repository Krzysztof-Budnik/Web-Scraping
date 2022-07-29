from pandas import read_csv


def performance(start: float, end: float, file_name: str) -> str:
    execution_time = end - start
    num_records = len(read_csv(file_name))
    time_per_record = execution_time / num_records

    message = f"""\nTotal execution time is: {execution_time:.2f} sec with {num_records} data records downloaded.
Program downloaded data at speed: {time_per_record:.2f} sec per one record\n"""
    return message