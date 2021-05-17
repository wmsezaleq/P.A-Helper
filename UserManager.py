from selenium import webdriver
from selenium.common.exceptions import WebDriverException 
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from tkinter import messagebox
from os import environ as os_environ
from traceback import format_exc as traceback_formatexc
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar as req_RequestsCookieJar
from requests import get as req_get
os_environ['WDM_LOG_LEVEL'] = '0' # Ocultar log de ChromeDRiverManager
os_environ['WDM_PRINT_FIRST_LINE'] = 'False' # Ocultar espacios de ChromeDriverManager
import requests
class User_Manager:
    jar = req_RequestsCookieJar()

    def __set_jarWithCookies(self, cookies):
        for cookie in cookies:
            self.jar.set(cookie["name"], cookie["value"], domain=cookie["domain"])

    def __init__(self):
        try:
            with open("data/user_data.dat","r") as file:
                self.__set_jarWithCookies(eval(file.read()))
        except:
            pass
    def get_username(self):
        soup = BeautifulSoup(requests.get("https://wms.mercadolibre.com.ar/", cookies=self.jar).text, features="lxml")
        username = ""
        try:
            username = soup.find('span', {"class":"kraken-nav__menu-user-mail"}).text
        except:
            username = "Ninguno"
        return username
    def login(self):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
            chrome_options.add_argument('log-level=3')

            driver = webdriver.Chrome(ChromeDriverManager(print_first_line=False).install(), options=chrome_options)
            driver.get("https://wms.mercadolibre.com.ar")
            sleep(1)
            while driver.current_url != "https://wms.mercadolibre.com.ar/":
                sleep(1)
            cookies = driver.get_cookies()
            driver.quit()
            with open("data/user_data.dat", "w") as file:
                file.write(str(cookies))
            self.__set_jarWithCookies(cookies)
        except WebDriverException:
            pass
        except KeyboardInterrupt:
            pass
        except:
            messagebox.showerror("ERROR", message=traceback_formatexc())
if __name__ == "__main__":
    AccountManager = User_Manager()
    t = AccountManager.get_username()
    print(t)
