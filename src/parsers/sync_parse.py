from utils.utils import *
from bs4 import BeautifulSoup as bs
import requests as req
from time import sleep

def sync_parse(url: str = 'https://quotes.toscrape.com/',
               retries: int = 3, retry_delay: int = 5, rm_chars: List[str] = ['”', '“'],
               ) -> List[Dict[str, Union[str, List[str]]]]:
    
    msg_started()

    all_quotes: List[Dict[str, Union[str, List[str]]]] = []
    is_end: bool = False
    quotes_count: int = 0
    page_num: int = 1

    while not is_end:
        msg_page_processing(page_num)

        attempt: int = 0
        resp: req.Response = None

        while attempt < retries:
            try:
                resp = req.get(f"{url}page/{page_num}/")
                resp.raise_for_status()
                break
            except req.RequestException as e:
                attempt += 1
                msg_request_error(attempt, retries, e)
                if attempt < retries:
                    msg_retry(retry_delay)
                    sleep(retry_delay)
                else:
                    msg_retries_reached()
                    return all_quotes

        soup = bs(resp.text, 'html.parser')

        el_quotes = soup.find_all(class_='quote')

        for el_quote in el_quotes:
            el_text = el_quote.find(class_='text')
            el_author = el_quote.find(class_='author')
            el_tags = el_quote.find(class_='tags')

            text: str = el_text.get_text(strip=True) if el_text else 'N/A'
            text = remove_chars(text, rm_chars)
            author: str = el_author.get_text(strip=True) if el_author else 'Unknown'
            tags: List[str] = [el_tag.get_text(strip=True) for el_tag in el_tags.find_all(class_='tag')] if el_tags else []

            all_quotes.append({'text': text, 'author': author, 'tags': tags})
            quotes_count += 1

        el_next_button = soup.select_one('nav .pager .next')
        if not el_next_button:
            is_end = True
            msg_pages_out()
        else:
            page_num += 1

    msg_quotes_count(quotes_count)
    msg_parsing_end()

    return all_quotes