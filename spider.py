import requests
from bs4 import BeautifulSoup
import time
import random

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = "http://quotes.toscrape.com/"
print("正在请求目标网站...")
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')
quotes = soup.find_all('div', class_='quote')

for quote in quotes:
    text = quote.find('span', class_='text').get_text()
    author = quote.find('small', class_='author').get_text()
    print(author + " 说: " + text)

print("抓取完成！")
time.sleep(1)
