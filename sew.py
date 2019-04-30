from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def getsource(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("C:\\Users\\X\\AppData\\Local\\Google\\Chrome\\User Data\\Default");
    options.add_argument('window-size=1900x1000')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    source=driver.page_source
    driver.close()
    return source
