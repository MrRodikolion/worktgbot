from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep

WINDOW_SIZE = '1920,1080'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)


def get_news():
    with webdriver.Chrome(options=chrome_options) as browser:
        browser.get('https://dzen.ru/news')
        sleep(3)

        all_news = []

        all_rubrics = browser.find_elements(By.CSS_SELECTOR, '[aria-label="Блок рубрики"]')
        for rubric in all_rubrics:
            news_block = rubric.find_element(By.CLASS_NAME, 'news-top-stories__others')

            news = news_block.find_elements(By.CLASS_NAME, 'news-top-stories__other')

            news_block_content = [{'href': n.find_element(By.CLASS_NAME, 'Link').get_attribute('href'),
                                   'text': n.text}
                                  for n in news if n.text]

            news_cards_block = rubric.find_element(By.CSS_SELECTOR, '[data-testid="top-cards"]')
            news_cards = news_cards_block.find_elements(By.CLASS_NAME, 'mg-card__shown-card')

            news_cards_content = [{'href': n.find_element(By.CLASS_NAME, 'Link').get_attribute('href'),
                                   'text': n.find_element(By.CLASS_NAME, 'news-card2-redesign__title').text}
                                  for n in news_cards]

            all_news += news_cards_content + news_block_content
        return all_news


def get_1img(url):
    with webdriver.Chrome(options=chrome_options) as browser:
        browser.get(url)
        sleep(3)

        first_img = browser.find_element(By.TAG_NAME, 'img')
        first_img_src = first_img.get_attribute('src')

        return first_img_src


if __name__ == '__main__':
    from pprint import pp

    pp(get_1img('https://dzen.ru/news/story/67c17cb7-ec6d-56e7-adf9-2002422e35c5?lang=ru&rubric=index&fan=1&t=1711727958&tt=true&persistent_id=2772981101&cl4url=843d4c5787cdfd8ae972c8813cb6f08d&story=fc2ba6b0-dd44-5ec7-ba35-ee48e4148785'))
