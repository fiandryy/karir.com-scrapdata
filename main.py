import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.karir.com/search?'
site = 'https://www.karir.com/'
params = {
    'context': 'welcome_main_search',
    'q': 'Sales',
    'location': 'Jakarta'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/113.0.0.0 Safari/537.36'}

res = requests.get(url, params=params, headers=headers)

def get_total_pages(query, location):
    params = {
        'context': 'welcome_main_search',
        'q': query,
        'location': location
    }

    res = requests.get(url, params=params, headers=headers)

    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    with open('temp/res.html', 'w+') as outfile:
        outfile.write(res.text)
        outfile.close()

    #scraping total_pages
    total_pages = []
    soup = BeautifulSoup(res.text, 'html.parser')
    pagination = soup.find('div', 'search-pagination sticky-search-stopper')
    pagination = pagination.ul
    pages = pagination.find_all('li')
    for page in pages:
        total_pages.append(page.text)

    total_pages = total_pages[2:9]
    total_pages = int(max(total_pages))
    return total_pages

def get_all_items(query, location, page):
    params = {
        'context': 'welcome_main_search',
        'q': query,
        'location': location
    }

    res = requests.get(url, params=params, headers=headers)

    with open('temp/res.html', 'w+') as outfile:
        outfile.write(res.text)
        outfile.close()
    soup = BeautifulSoup(res.text, 'html.parser')

    #scraping item
    contents = soup.find('ul', 'opportunities')
    contents = contents.find_all('li', 'columns opportunity')

    job_list = []
    for item in contents:
        job_title = item.find('h4', 'tdd-function-name --semi-bold --inherit').text
        company_name = item.find('div', 'tdd-company-name h8 --semi-bold').text
        post_date = item.find('time').text
        try:
            job_link = site + item.find('a')['href']
        except:
            job_link = 'Link is not available'

        data_dict = {
            'job title' : job_title,
            'company name' : company_name,
            'post date' : post_date,
            'job link' : job_link
        }
        job_list.append(data_dict)

    #writing json file
    try:
        os.mkdir('json_result')
    except FileExistsError:
        pass

    with open(f'json_result/{query}_in_{location}_page_{page}.json', 'w+') as json_data:
        json.dump(job_list, json_data)
    print('json created')
    return job_list

def create_document(dataFrame, Filename):
    try:
        os.mkdir('data_result')
    except FileExistsError:
        pass

    df = pd.DataFrame(dataFrame)
    df.to_csv(f'data_result/{Filename}.csv', index=False)
    df.to_excel(f'data_result/{Filename}.xlsx', index=False)

    print(f'file {Filename}.csv and {Filename}.xlsx is successfully created')

def run():
    query = input('Enter your Query: ')
    location = input('Enter the Location: ')
    total = get_total_pages(query, location)

    final_result = []
    for page in range(total):
        page += 1
        final_result += get_all_items(query, location, page)

    #formatting data
    try:
        os.mkdir('reports')
    except FileExistsError:
        pass

    with open('reports/{}.json'.format(query), 'w+') as final_data:
        json.dump(final_result, final_data)

    print('Data JSON Has Been Created')

    #create document
    create_document(final_result, query)

if __name__ == '__main__':
    run()
