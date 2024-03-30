import config
from parsing import get_news, get_1img

import sqlite3
import asyncio
import logging
import pymorphy2
import string

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

con = sqlite3.connect('created_posts.db')
cur = con.cursor()


def get_first_verb(text):
    morph = pymorphy2.MorphAnalyzer()
    words = text.split()
    for word in words:
        p = morph.parse(word.lower())[0]
        if 'VERB' in p.tag:
            return word
    return None


async def post_creation():
    while True:
        news = get_news()
        existed_news = cur.execute('''SELECT url FROM urls''').fetchall()
        existed_news = [en[0] for en in existed_news]
        for n in news:
            url_story = n['href'][n['href'].rfind('url'):]

            morph = pymorphy2.MorphAnalyzer()
            translator = str.maketrans('', '', string.punctuation)

            normal_text = n['text'].translate(translator)
            normal_text = [morph.parse(word)[0].normal_form.lower() for word in normal_text.split()]

            if (url_story not in existed_news and
                    any(morph.parse(word)[0].normal_form.lower() in normal_text for word in config.words)):
                verb = get_first_verb(n['text'])
                if verb:
                    before_verb, after_verb = n['text'].split(verb, maxsplit=1)
                    message_text = f'{before_verb}<a href=\"{n["href"]}\">{verb}</a>{after_verb}'
                else:
                    word, after_word = n['text'].split(maxsplit=1)
                    message_text = f'<a href=\"{n["href"]}\">{word}</a>{after_word}'

                cur.execute(f'''INSERT INTO urls (url) VALUES(\"{url_story}\");''')

                await bot.send_photo(config.chat_id, photo=get_1img(n['href']), caption=message_text)
                con.commit()
        await asyncio.sleep(config.delay)


async def main():
    cur.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id integer  PRIMARY KEY,
                    url text
                    );''')
    con.commit()

    await bot.delete_webhook(drop_pending_updates=True)

    await asyncio.create_task(post_creation())

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='log.txt')
    asyncio.run(main())
    con.close()
