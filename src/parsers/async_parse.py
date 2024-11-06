import aiohttp
import asyncio
from utils.utils import *
from bs4 import BeautifulSoup as bs
from typing import List, Dict, Union

async def fetch(session, url: str, retries: int = 3, retry_delay: int = 5) -> str:
    attempt = 0

    while attempt < retries:
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.text()
        except aiohttp.ClientError as e:
            attempt += 1
            msg_request_error(attempt, retries, e)
            if attempt < retries:
                await asyncio.sleep(retry_delay)
            else:
                msg_retries_reached()
                return ''

async def parse_page(url: str, rm_chars: List[str] = ['”', '“']):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)

        if not html:
            return {'quotes': [], 'is_last_page': True}

        try:
            soup = bs(html, 'html.parser')
            el_quotes = soup.find_all(class_='quote')
        except Exception as e:
            print(f"Error parsing the page {url}: {e}")
            return {'quotes': [], 'is_last_page': True}

        if not el_quotes:
            return {'quotes': [], 'is_last_page': True}

        quotes = []
        for el_quote in el_quotes:
            el_text = el_quote.find(class_='text')
            el_author = el_quote.find(class_='author')
            el_tags = el_quote.find(class_='tags')

            text = el_text.get_text(strip=True) if el_text else 'N/A'
            text = remove_chars(text, rm_chars)
            author = el_author.get_text(strip=True) if el_author else 'Unknown'
            tags = [el_tag.get_text(strip=True) for el_tag in el_tags.find_all(class_='tag')] if el_tags else []

            quotes.append({
                'text': text,
                'author': author,
                'tags': tags
            })

        next_button = soup.select_one('nav .pager .next')
        is_last_page = False if next_button else True

        return {
            'quotes': quotes,
            'is_last_page': is_last_page
        }

async def async_parse(url: str = 'https://quotes.toscrape.com/',
               retries: int = 3, retry_delay: int = 5, rm_chars: List[str] = ['”', '“'],
               parallel_tasks: int = 10) -> List[Dict[str, Union[str, List[str]]]]:

    msg_started()

    quotes = []
    is_end: bool = False
    quotes_count: int = 0
    page_num: int = 1

    async with aiohttp.ClientSession() as session:
        tasks = []

        while not is_end:
            msg_page_processing(page_num)
            task = asyncio.create_task(parse_page(f"{url}page/{page_num}", rm_chars))
            tasks.append(task)
            page_num += 1

            if len(tasks) >= parallel_tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for res in results:
                    if isinstance(res, Exception):
                        print(f"Error during page parsing: {res}")
                        continue

                    quotes_count += len(res['quotes'])
                    quotes.extend(res['quotes'])

                    if res['is_last_page']:
                        is_end = True
                        msg_pages_out()
                        break
                tasks = []

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    print(f"Error during page parsing: {res}")
                    continue

                quotes_count += len(res['quotes'])
                quotes.extend(res['quotes'])

                if res['is_last_page']:
                    is_end = True
                    msg_pages_out()
                    break

    msg_quotes_count(quotes_count)
    msg_parsing_end()
    return quotes