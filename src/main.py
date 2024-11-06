import argparse
import asyncio
from time import time
from utils.utils import quotes_to_json

parser = argparse.ArgumentParser(
    description='''Specify the parsing type as a command-line argument:\n
    sync - synchronous parsing
    async - asynchronous parsing (default)
    all - runs all parsing methods (x2 parsing)''',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    "--type", 
    type=str, 
    choices=["sync", "async", "all"], 
    default="async", 
    help="Type of parsing to use"
)

settings = {
    'url': 'https://quotes.toscrape.com/',
    'req_retries': 3,
    'retry_delay': 5,
    'remove_chars': ['”', '“'],
    'async_tasks': 10
}

if __name__ == '__main__':
    args = parser.parse_args()
    start_time = time()
    quotes = []

    print(f"Selected type: {args.type}\n")

    if args.type in ['sync', 'all']:
        '''Synchronous parsing'''
        import parsers.sync_parse as syncp

        quotes = syncp.sync_parse(
            url=settings['url'],
            retries=settings['req_retries'],
            retry_delay=settings['retry_delay'],
            rm_chars=settings['remove_chars']
        )

        file_prefix = 'sync'

    if args.type == 'all':
        '''Write the result of synchronous parsing if the type all is selected'''
        if len(quotes):
            quotes_to_json(f"{file_prefix}_quotes", quotes)
        else:
            print(f"Empty data")

        end_time = time()
        print(f"Execution time: {end_time - start_time:.4f} seconds\n")
        start_time = time()

    if args.type in ['async', 'all']:
        '''Asynchronous parsing'''
        import parsers.async_parse as asyncp

        quotes = asyncio.run(asyncp.async_parse(
            url=settings['url'],
            retries=settings['req_retries'],
            retry_delay=settings['retry_delay'],
            rm_chars=settings['remove_chars'],
            parallel_tasks=settings['async_tasks']
        ))

        file_prefix = 'async'

    if len(quotes):
        quotes_to_json(f"{file_prefix}_quotes", quotes)
    else:
        print(f"Empty data")
        
    end_time = time()
    print(f"Execution time: {end_time - start_time:.4f} seconds")