import auth_data
import requests
from bs4 import BeautifulSoup
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from sqlighter import SQLighter
from states import states_1
import asyncio
from dict import dict_reverse
# инициализируем бота
bot = Bot(token=auth_data.token)
dp = Dispatcher(bot,storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# инициализируем соединение с БД
db = SQLighter('db.db')


# Команда активации подписки
@dp.message_handler(commands=['subs'])
async def subscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)

    await message.answer(
        "Вы успешно подписались на рассылку!\nЖдите, скоро выйдут новые обзоры и вы узнаете о них первыми =)")


# Команда отписки
@dp.message_handler(commands=['unsubs'])
async def unsubscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")



@dp.message_handler(content_types='text')
async def send_text(message: types.Message):
    try:
        if message.text:
            url_book = message.text
        url = url_book
        page_url = '/page/'
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
        }
        req = requests.get(url=url, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')
        next_page = soup.find("div", class_='item__point-list pagination').find_all('a', class_='page-numbers')[1].get(
            'href')
        print(next_page)
        npages = next_page.split(url)[1].split('page/')[1].split('/')[0]
        count = 1
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
            await message.answer("Книга почти готова")
            # Подгрузка файла со страницами
            with open(f"json/page.json", encoding='utf8') as file:
                all_pages = json.load(file)
            # Перебераем страницы сайта и записываем и читаем
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
                    # Перебераем страницы с главами и записываем файл
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
                            file.close()


                count += 1


            await message.answer("Книга готова ввидите название: ")
            await states_1.Name_book.set()
    except Exception as ex:
        print(ex)

@dp.message_handler(state=states_1.Name_book)
async def name_book(message:types.Message, state:FSMContext):
    try:
        if message.text:
            name_book = message.text
            os.rename(r"books\default.fb2", rf"books\{name_book}.fb2")
            f =open(rf"books\{name_book}.fb2", "rb")
        await bot.send_document(message.chat.id, f)
        await state.finish()



    except Exception as ex:
            print(ex)

async def new_books(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        subscriptions = db.get_subscriptions()


        url = 'https://ranobelib.ru'
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
        }
        req = requests.get(url, headers=headers)
        src = req.text
        soup = BeautifulSoup(src, "lxml")
        links = soup.find("div", class_='col-xs-12 new_books').find_all('a', class_='img')
        print(type(links))
        imgs = soup.find("div", class_='row block_content').find_all('img')
        link = []
        img = []
        title  = []
        for ind in links:
            link.append(ind.get('href'))
            print(link)
        for i in imgs:
            img.append(i.get('src'))
            title.append(i.get('title'))

        for s in subscriptions:
            for j in range(len(link)):
                await bot.send_photo(s[1], img[j], caption="Новоя книга возможно вам будет интересно"+'\n'+title[j] + "\n" + str(link[j]))


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(new_books(10000000))
    executor.start_polling(dp, skip_updates=True,on_shutdown=shutdown)