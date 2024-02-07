import time
import requests
from bs4 import BeautifulSoup as bs
import re
from string import ascii_lowercase

men_names = [f'male_{i}_names' for i in ascii_lowercase]
woman_names = [f'female_{i}_names' for i in ascii_lowercase]
csv_file_name = 'names_m.csv'
parsed_names_list = men_names


def get_and_save(so_up):
    page = [j.find('b') for j in so_up.find_all('li')]
    pattern = r'<a name="([^"]+)">|>([^<]+)<'
    list_of_names = [match[0] if match[0] else match[1] for j in page for match in re.findall(pattern, str(j))]
    pattern = r'\b[A-Z]{2,}(?:-[A-Z]+)*\b'
    pure_names = [j.group() for i in list_of_names if (j := re.fullmatch(pattern, i))]
    with open(csv_file_name, 'a', encoding='utf-8') as f:
        _ = [f.write(i + ',') for i in pure_names if i]


def count_of_pages(so_up, na_me):
    count_ = 0
    try:
        phrase = na_me + r'_\d+\.htm'
        all_find = [itm for itm in [i.get('href') for i in so_up.find_all('a')] if itm is not None and re.match(phrase, itm)] # noqa
        count_ = int(all_find[-1:][0].split('.')[0].split('_')[-1:][0])
    except Exception as e:
        count_ = 0
    finally:
        return count_


for name in parsed_names_list:
    url = f'https://www.20000-names.com/{name}.htm'
    responce1 = requests.get(url)
    soup = bs(responce1.text, 'html.parser')
    get_and_save(soup)

    '''Ищем кличество страниц с именами, если их нет count_pages=0 и цикл for не стартует'''
    count_pages = count_of_pages(soup, name)

    for count in range(2, count_pages+1):
        url2 = f'https://www.20000-names.com/{name}_{count}.htm'
        responce2 = requests.get(url2)
        soup2 = bs(responce2.text, 'html.parser')
        get_and_save(soup2)
        time.sleep(5)
