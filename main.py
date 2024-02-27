import json
import datetime
import aiohttp
import asyncio
import sys
from datetime import timedelta

async def get_exchange_rate(date):
    url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                raise Exception(f"Failed to fetch data for {date}. Status code: {response.status}")

async def get_exchange_rates_for_last_n_days(n):
    current_date = datetime.date.today()
    exchange_rates = []

    for _ in range(n):
        formatted_date = current_date.strftime('%d.%m.%Y')
        data = await get_exchange_rate(formatted_date)
        
        exchange_rate_data = data.get('exchangeRate', [])
        
        if exchange_rate_data:
            rates = {
                formatted_date: {
                    'EUR': {
                        'sale': exchange_rate_data[0].get('saleRateNB', 0),
                        'purchase': exchange_rate_data[0].get('purchaseRateNB', 0)
                    },
                    'USD': {
                        'sale': exchange_rate_data[1].get('saleRateNB', 0),
                        'purchase': exchange_rate_data[1].get('purchaseRateNB', 0)
                    }
                }
            }
            exchange_rates.append(rates)
        else:
            print(f"No exchangeRate data for {formatted_date}")

        current_date -= timedelta(days=1)

    # Зберігаємо дані у файл JSON
    output_file_path = 'exchange_rates.json'
    with open(output_file_path, 'w') as file:
        json.dump(exchange_rates, file)
        print(f"Exchange rates saved to: {output_file_path}")

    return exchange_rates

def print_usage():
    print("Usage: python main.py <number_of_days>")
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print_usage()

    try:
        num_days = int(sys.argv[1])
        if num_days <= 0 or num_days > 10:
            raise ValueError("Number of days should be between 1 and 10")
    except ValueError:
        print("Invalid input. Please provide a valid number of days.")
        print_usage()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_exchange_rates_for_last_n_days(num_days))
