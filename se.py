from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def getsource(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("user-data-dir=/Users/AltX/Library/Application Support/Google/Chrome/Default");
    options.add_argument('window-size=1900x1000')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    source=driver.page_source
    driver.close()
    return source
