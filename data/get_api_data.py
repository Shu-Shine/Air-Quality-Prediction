import time
import requests
from bs4 import BeautifulSoup
import re

def generate_url(category, city, year, month):
    if category == 'air':
        return f'http://www.tianqihoubao.com/aqi/{city}-{year}{str("%02d" % month)}.html'
    elif category == 'weather':
        return f'http://www.tianqihoubao.com/lishi/{city}/month/{year}{str("%02d" % month)}.html'
    return None

def extract_air_data(td):
    field_names = ['Date', 'Quality_grade', 'AQI', 'AQI_rank', 'PM', 'PM10', 'So2', 'No2', 'Co', 'O3']
    data_dict = {field_names[i]: td[i].get_text().strip() for i in range(len(field_names))}
    # month = re.search(r"\d{4}-(\d{2})-\d{2}", data_dict['Date']).group(1)
    # data_dict['Month'] = month
    return data_dict

def extract_weather_data(td):
    date = td[0].get_text().strip()
    month = re.search(r"\d{4}年(\d{2})月\d{2}日", date).group(1)
    weather_day, weather_night = map(str.strip, td[1].get_text().split('/'))
    temp_max, temp_min = [t.strip().replace('℃', '') for t in td[2].get_text().split('/')]
    wind_day, wind_night = [w.strip().split(' ') for w in td[3].get_text().split('/')]
    
    return {
        'Date': date,
        'Weather_day': weather_day,
        'Weather_night': weather_night,
        'Temp_max': temp_max,
        'Temp_min': temp_min,
        'WindDirection_day': wind_day[0].strip(),
        'WindSpeed_day': wind_day[1].strip().replace('级', ''),
        'WindDirection_night': wind_night[0].strip(),
        'WindSpeed_night': wind_night[1].strip().replace('级', ''),
        'Month': month,
    }

def save_to_csv(category, city, year, data_dict):
    with open(f'{category}_{city}_{year}.csv', 'a+', encoding='gb2312') as f:
        f.write(','.join(data_dict.values()) + '\n')

def download_data(category, city, year):
    headers = {
        'User-Agent':''
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for month in range(1, 13):  # Loop through all months
        time.sleep(5)  # Avoid accessing too frequently
        url = generate_url(category, city, year, month)

        response = requests.get(url=url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve data for {category} in {city} for month {month}: {response.status_code}")
            continue  # Skip to the next month if the request fails

        soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content
        tr = soup.find_all('tr')  # Find the table rows

        for j in tr[1:]:  # Skip the header row
            td = j.find_all('td')
            if category == 'air':
                if len(td) < 10:
                    print(f"Not enough data in air quality for {city} in {year}-{month:02d}. Skipping...")
                    continue  # Ensure there are enough columns
                data_dict = extract_air_data(td)
            elif category == 'weather':
                if len(td) < 4:
                    print(f"Not enough data in weather for {city} in {year}-{month:02d}. Skipping...")
                    continue  # Ensure there are enough columns
                data_dict = extract_weather_data(td)

            save_to_csv(category, city, year, data_dict)

if __name__ == '__main__':
    # with open('cities.txt', 'r', encoding='utf-8') as f:
    #     cities = [line.strip() for line in f.readlines() if line.strip()]  # Read lines and strip whitespace
    
    cities = ['shanghai']
     
    years = range(2018, 2019)  # Years from 2013 to 2018

    for city in cities:
        for year in years:
            # download_data('air', city, year)
            download_data('weather', city, year)

    print("Data download complete.")


