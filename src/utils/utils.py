from re import sub, escape
from typing import Dict, List, Union
from datetime import datetime
import json

def remove_chars(text: str, chars: List[str]) -> str:
    pattern: str = f"[{''.join(map(escape, chars))}]"
    return sub(pattern, '', text)

def quotes_to_json(out_name: str, quotes: List[Dict[str, Union[str, List[str]]]]):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d-%m-%Y-%H-%M-%S")

    with open(f'{out_name}_{formatted_time}.json', 'w', encoding='utf-8') as f:
        json.dump(quotes, f, ensure_ascii=True, indent=4)

def msg_started() -> None:
    print('Parsing started.')

def msg_page_processing(page_num: int) -> None:
    print(f"Page {page_num} in process...")

def msg_pages_out() -> None:
    print("Pages are out.")

def msg_quotes_count(quotes_count: int) -> None:
    print(f"Parsed quotes count: {quotes_count}")

def msg_parsing_end() -> None:
    print("Successful parse end")

def msg_request_error(attempt: int, retries: int, e: Exception):
    print(f"Error during request (attempt {attempt}/{retries}): {e}")

def msg_retry(retry_delay: int):
    print(f"Retrying in {retry_delay} seconds...")

def msg_retries_reached():
    print("Max retries reached. Exiting.")