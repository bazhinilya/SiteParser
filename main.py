from requests import get
from bs4 import BeautifulSoup
import re
from wordcloud import WordCloud
import docx
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://www.np-sr.ru'
URL = f'{BASE_URL}/ru/regulation/joining/reglaments/index.htm'
HEADERS = {
    'Accept': 'text/html',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
}

def fetch_page(url):
    response = get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    return response.text

def extract_regulations(soup):
    regulations = {}
    page_elements = soup.find_all(class_='border-content-box border-content-box--offset border-content-box--brown border-content-box--hover flex flex--a-center flex--j-between typography')
    
    for element in page_elements:
        regulation = element.find('div').text.strip()
        reference = element.find('a').get('href')
        print(f'__{regulation}\n')
        regulation_number = re.findall(r'\d+', regulation)
        if regulation_number:
            regulations[regulation_number[0]] = reference
    return regulations

def get_regulation_url(regulations, input_regulation):
    key = re.findall(r'\d+', input_regulation)
    return regulations.get(key[0]) if key else None

def download_document(url, filename):
    response = get(url, headers=HEADERS, stream=True, verify=False)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)

def generate_wordcloud(text, filename):
    cloud = WordCloud().generate(text)
    cloud.to_file(f'{filename}.pdf')

def main():
    soup = BeautifulSoup(fetch_page(URL), 'lxml')
    print(f'{soup.title.text.split(".")[0]}:')
    regulations = extract_regulations(soup)

    while True:
        input_regulation = input('\nВведите номер документа или название документа\n')
        url_regulation = get_regulation_url(regulations, input_regulation)
        if url_regulation:
            break
        print('Некорректный номер документа или название документа\n')

    document_url = f'{BASE_URL}{url_regulation}'
    soup = BeautifulSoup(fetch_page(document_url), 'lxml')
    URL_DOC = soup.find(class_='doc__item doc__col col col--top w-50').find('a').get('href')
    
    filename = 'file.docx'
    download_document(URL_DOC, filename)

    doc = docx.Document(filename)
    text = ''.join(paragraph.text for paragraph in doc.paragraphs)
    generate_wordcloud(text, 'worldcloud')
    print('Облако слов успешно получено\n')

if __name__ == '__main__':
    main()