import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import json
import os
from auth_data import token
def dict_reverse(dict):
    revDict = {}
    d = list(dict.keys())
    d.reverse()
    for str in d:
        revDict[str] = dict[str]
    return revDict

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    # Приветствие пользователя
    @bot.message_handler(commands=['start'])
    def start_massage(message):
        bot.send_message(message.chat.id, "Привет Странник")

    @bot.message_handler(content_types='text')
    def send_text(message):
        if message.text:
            try:
                url_book = message.text
                url = url_book
                page_url = '/page/'
                headers = {
                    "Accept": "*/*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
                }
                count = 1
                req = requests.get(url, headers=headers)
                src = req.text
                soup = BeautifulSoup(src, "lxml")
                # Определяем количество страниц

                next_page = soup.find("div", class_='item__point-list pagination').find_all('a', class_='page-numbers')[1].get('href')
                npages = next_page.split(url)[1].split('page/')[1].split('/')[0]

                # Запись всех ссылок страниц в файл
                all_page = {}
                with open(f"json/page.json", "w", encoding='utf8') as file:
                    for i in range(1, 0, -1):
                        url_page = requests.get(url + page_url + str(i))
                        src = url_page.url
                        item_href = src
                        all_page[str(i)] = item_href
                        i += 1
                        print(all_page)
                    json.dump(all_page, file, indent=4, ensure_ascii=False)
                    file.close()
                bot.send_message(message.chat.id, "Книга почти готова")
                # Подгрузка файла со страницами
                with open(f"json/page.json", encoding='utf8') as file:
                    all_pages = json.load(file)
                #Перебераем страницы сайта и записываем и читаем
                for name_page, href_page in all_pages.items():
                    req = requests.get(url=href_page, headers=headers)
                    src1 = req.text
                    with open(f"pages/{count}_.html", "w", encoding='utf-8') as file:
                        file.write(src1)
                    with open(f"pages/{count}_.html", "r", encoding='utf-8') as file:
                        src1 = file.read()
                        soup = BeautifulSoup(src1, 'lxml')
                        all_products_href = soup.find_all("a", class_="ttl")
                        all_glav_s = {}
                        for item in all_products_href:
                            item_text = item.get('href').split('/')[4]
                            item_href = item.get('href')
                            all_glav_s[item_text] = item_href
                            with open(f"json/{count}_page.json", "w", encoding='utf-8') as file:
                                json.dump(dict_reverse(all_glav_s), file, indent=4, ensure_ascii=False)
                    with open(f"json/{count}_page.json", encoding='utf8') as file:
                        all_glav_p = json.load(file)
                        #Перебераем страницы с главами и записываем файл
                        for glav_name, glavs_href in all_glav_p.items():
                            req = requests.get(url=glavs_href, headers=headers)
                            src = req.text
                            with open(f"pages/{count}_1.html", "w", encoding='utf8') as file:
                                file.write(src)
                            with open(f"pages/{count}_1.html", "r", encoding='utf-8') as file:
                                src = file.read()
                                soup = BeautifulSoup(src, "lxml")
                                text_title = soup.find("div", class_="title")
                                text = soup.find(class_="text")

                            with open(f"books/default.fb2", "a", encoding='utf8') as file:
                                file.write(str(text_title.text))
                                file.write(str(text.text))

                    count += 1
                bot.send_message(message.chat.id, "Введите название книги: ")
                message = bot.register_next_step_handler(message, name_book)
            except Exception as ex:
                print(ex)

    def name_book(message):
        try:
            if message.text:
                name_book = message.text
                os.rename(r"books\default.fb2", rf"books\{name_book}.fb2")
                f = open(rf"books\{name_book}.fb2", "rb")
                url ='https://ranobelib.ru'
                headers = {
                    "Accept": "*/*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
                }
                req = requests.get(url, headers=headers)
                src = req.text
                soup = BeautifulSoup(src, "lxml")
                link = soup.find("a", class_='img')
                imgs = soup.find("div", class_='row block_content').find_all('img')
                for item            bot.send_photo(message.chat.id, img, caption=title)


                bot.send_document(message.chat.id, f)
        except Exception as ex:
            print(ex)





    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)
