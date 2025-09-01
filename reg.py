import os
import sys
import jwt
import sqlite3
import time
import requests
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import platform
from collections import defaultdict
import random
import re
from typing import List, Tuple, Optional
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UgphoneRegistration:
    def __init__(self):
        self.driver = None
        self.waitTime = 5
        self.maxRetries = 3
        self.userToken = "H9G7R8JLGG9Y795YCFSNB2PMY5S7R74DANKH"
        self.kioskToken = "JSYPAXDKPHRLR6T8DN2W"
        self.proxies = []
        self.loadProxies()
        self.system = platform.system().lower()
        self.accounts_file = 'accounts.txt'

    def loadProxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error("No proxies.txt file found!")

    def loadAccounts(self):
        try:
            with open(self.accounts_file, 'r') as f:
                accounts = [line.strip() for line in f if line.strip()]
            return accounts
        except FileNotFoundError:
            logger.error("No accounts.txt file found!")
            return []

    def getRandomProxy(self):
        while self.proxies:
            proxy = random.choice(self.proxies)
            if self.verifyProxy(proxy):
                return proxy
            self.proxies.remove(proxy)
        return None

    def verifyProxy(self, proxy):
        try:
            response = requests.get('http://ip-api.com/json',
                proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}, timeout=5)
            return response.status_code == 200
        except:
            return False

    def setupDriver(self, proxy=None):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        if self.system == 'linux' and 'TERMUX_VERSION' in os.environ:
            options.add_argument('--headless')
            options.add_argument('--disable-setuid-sandbox')
            chromeDriverPath = '/data/data/com.termux/files/usr/bin/chromedriver'
            if os.path.exists(chromeDriverPath):
                service = Service(chromeDriverPath)
            else:
                service = Service(ChromeDriverManager().install())
        else:
            service = Service(ChromeDriverManager().install())

        options.add_argument('--window-size=412,915')
        options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36')
        options.add_argument('--incognito')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')

        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def safeClick(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            ActionChains(self.driver).move_to_element(element).click().perform()
            return True
        except:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False

    def findElement(self, locators, clickable=False):
        wait = WebDriverWait(self.driver, self.waitTime)
        for by, value in locators:
            try:
                element = wait.until(EC.element_to_be_clickable((by, value)) if clickable
                    else EC.presence_of_element_located((by, value)))
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def waitForPageLoad(self):
        try:
            WebDriverWait(self.driver, self.waitTime).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)
            return True
        except:
            return False

    def acceptTerms(self):
        termsLocators = [
            (By.XPATH, "//button[contains(text(), 'Accept')]"),
            (By.XPATH, '//*[@id="app"]/div/div/div/div[3]/div/div/i'),
            (By.CSS_SELECTOR, '.terms-accept-button')
        ]
        time.sleep(1)
        element = self.findElement(termsLocators, clickable=True)
        if element and self.safeClick(element):
            time.sleep(1)
            return True
        return False

    def clickGoogleLogin(self):
        googleLocators = [
            (By.XPATH, "//button[contains(., 'Google')]"),
            (By.XPATH, '//*[@id="app"]/div/div/div/div[2]/div/div[1]/div/button[1]'),
            (By.CSS_SELECTOR, '.google-login-button')
        ]
        time.sleep(1)
        element = self.findElement(googleLocators, clickable=True)
        if element and self.safeClick(element):
            time.sleep(2)
            handles = self.driver.window_handles
            if len(handles) > 1:
                self.driver.switch_to.window(handles[-1])
            return True
        return False

    def loginGoogle(self, email, password):
        emailLocators = [
            (By.CSS_SELECTOR, 'input[type="email"]'),
            (By.NAME, "identifier"),
            (By.XPATH, "//input[@type='email']")
        ]
        time.sleep(2)
        emailInput = self.findElement(emailLocators)
        if not emailInput:
            return False

        emailInput.clear()
        emailInput.send_keys(email)

        nextLocators = [
            (By.CSS_SELECTOR, '#identifierNext button'),
            (By.XPATH, "//button[contains(., 'Next')]"),
            (By.XPATH, "//div[@id='identifierNext']//button")
        ]

        nextButton = self.findElement(nextLocators, clickable=True)
        if not nextButton or not self.safeClick(nextButton):
            return False

        time.sleep(3)

        passwordLocators = [
            (By.CSS_SELECTOR, 'input[type="password"]'),
            (By.NAME, "password"),
            (By.XPATH, "//input[@type='password']")
        ]

        passwordInput = self.findElement(passwordLocators)
        if not passwordInput:
            return False

        passwordInput.clear()
        passwordInput.send_keys(password)

        passwordNextLocators = [
            (By.CSS_SELECTOR, '#passwordNext button'),
            (By.XPATH, "//button[contains(., 'Next')]"),
            (By.XPATH, "//div[@id='passwordNext']//button")
        ]

        passwordNext = self.findElement(passwordNextLocators, clickable=True)
        if not passwordNext or not self.safeClick(passwordNext):
            return False

        time.sleep(3)

        confirmLocators = [
            (By.ID, 'confirm'),
            (By.XPATH, "//button[contains(., 'Confirm')]"),
            (By.XPATH, '//*[@id="confirm"]')
        ]

        confirmButton = self.findElement(confirmLocators, clickable=True)
        if confirmButton:
            self.safeClick(confirmButton)

        time.sleep(2)

        continueLocators = [
            (By.XPATH, "//button[contains(., 'Continue')]"),
            (By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[3]/div/div/div[2]/div/div/button'),
            (By.CSS_SELECTOR, '.continue-button')
        ]

        continueButton = self.findElement(continueLocators, clickable=True)
        if continueButton:
            self.safeClick(continueButton)

        time.sleep(3)
        return True

    def buyAccounts(self, quantity=1):
        url = f"https://taphoammo.net/api/buyProducts?kioskToken={self.kioskToken}&userToken={self.userToken}&quantity={quantity}"
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("success") == "true":
                return data.get("order_id")
            return None
        except Exception as e:
            logger.error(f"{str(e)}")
            return None

    def getAccounts(self, orderId):
        url = f"https://taphoammo.net/api/getProducts?orderId={orderId}&userToken={self.userToken}"
        maxAttempts = 5
        attempt = 0

        while attempt < maxAttempts:
            try:
                response = requests.get(url)
                data = response.json()

                if data.get("success") == "true":
                    accounts = [account["product"] for account in data.get("data", [])]
                    return accounts[0] if accounts else None
                elif "Order in processing" in data.get("description", ""):
                    attempt += 1
                    time.sleep(2)
                    continue
                return None
            except Exception as e:
                logger.error(f"{str(e)}")
                return None
        return None

    def getLocalStorage(self):
        try:
            localStorage = self.driver.execute_script("""
                let items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            """)
            return localStorage
        except Exception as e:
            logger.error(f"Error getting localStorage: {str(e)}")
            return {}

    def submitInvitationCode(self, mqtt_data):
        try:
            if isinstance(mqtt_data, str):
                mqtt_data = json.loads(mqtt_data)

            login_id = mqtt_data.get('login_id')
            access_token = mqtt_data.get('access_token')

            if not login_id or not access_token:
                logger.error("Missing MQTT DATA")
                return False

            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/json;charset=UTF-8',
                'access-token': access_token,
                'login-id': login_id,
                'terminal': 'web',
                'lang': 'en',
                'update-date': time.strftime('%Y%m%d'),
                'Origin': 'https://www.ugphone.com',
                'Referer': 'https://www.ugphone.com/toc-portal/'
            }

            payload = {
                "invitation_code": "Ugminh"
            }

            response = requests.post(
                'https://www.ugphone.com/api/apiv1/user/bindInvitationCode',
                headers=headers,
                json=payload
            )

            response_data = response.json()

            if response_data.get('code') == 200 and response_data.get('msg') == 'Submitted successfully':
                logger.info("[ + ] Nhập Code Invited Thành Công")
                return True

            logger.error(f"[ - ] Fail : {response_data}")
            return False

        except Exception as e:
            logger.error(f"[ - ] Fail : {str(e)}")
            return False

    def completeRegistration(self, email, password):
        try:
            self.driver.get('https://www.ugphone.com/toc-portal/#/login')

            if not self.waitForPageLoad():
                return False

            if not self.acceptTerms():
                return False

            if not self.clickGoogleLogin():
                return False

            if not self.loginGoogle(email, password):
                return False

            mainWindow = self.driver.window_handles[0]
            self.driver.switch_to.window(mainWindow)

            time.sleep(5)

            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )

            localStorage = self.getLocalStorage()

            mqtt_data = localStorage.get('UGPHONE-MQTT')
            if mqtt_data:
                if not self.submitInvitationCode(mqtt_data):
                    logger.warning("FAIL INVITED CODE")

            if self.adez(localStorage):
                resultData = {
                    "email": email,
                    "password": password,
                    "localStorage": localStorage
                }
                self.registrationData = resultData
                logger.info(f"[ + ] Thành Công : {email}")
                return True
            else:
                logger.error(f"[ - ] Fail : {email}")
                return False

        except Exception as e:
            logger.error(f"[ - ] Fail : {str(e)}")
            return False

    def adez(self, localStorage):
        try:
            mqtt_data = json.loads(localStorage.get('UGPHONE-MQTT', '{}'))
            return 'mqtt_url' in mqtt_data and mqtt_data.get('is_visitor') == 0
        except Exception as e:
            logger.error(f"[ - ] Fail : {str(e)}")
            return False

    def register(self, quantity, thread_id):
        try:
            for _ in range(quantity):
                if MODEPROXY == 1:
                    orderId = self.buyAccounts()
                    if not orderId:
                        logger.error("[ - ] Fail : Mua mail không thành công.")
                        continue

                    logger.info("[ ! ] Mua mail, lấy thông tin.")

                    account = self.getAccounts(orderId)
                    if not account:
                        logger.error("[ - ] Fail : Lấy đơn hàng kh thành công.")
                        continue

                    email, password = account.split('|')

                else:
                    accounts = self.loadAccounts()
                    if not accounts:
                        logger.error("[ - ] Fail : không thấy acc trong accounts.txt")
                        continue

                    account = accounts.pop(0)
                    try:
                        email, password = account.split('|')
                        with open(self.accounts_file, 'w') as f:
                            f.write('\n'.join(accounts))
                    except ValueError:
                        logger.error("[ - ] Fail : lỗi định dạng accounts.txt")
                        continue

                proxy = self.getRandomProxy()
                if not proxy:
                    logger.error("[ - ] Fail: Đéo có proxy")
                    continue

                logger.info(f"[ + ] Thread {thread_id} Bắt đầu reg")

                self.setupDriver(proxy)
                success = self.completeRegistration(email, password)

                if success and hasattr(self, 'registrationData'):
                    localStorageStr = json.dumps(self.registrationData['localStorage'])
                    with open('registrations.txt', 'a') as f:
                        f.write(f"{email}|{password}|{localStorageStr}\n")
                    logger.info(f"[ + ] Thread {thread_id} Thành Công : {email}")
                else:
                    logger.error(f"[ - ] Thread {thread_id} Fail : Fail reg")

        except Exception as e:
            logger.error(f"[ - ] Thread {thread_id} Fail: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ugphone Registration Tool")
    parser.add_argument('--quantity', type=int, required=True, help='Số lượng acc cần reg')
    parser.add_argument('--mode', type=int, choices=[1, 2], required=True, help='Mode: 1 for API, 2 for Text File')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads to use')
    args = parser.parse_args()

    MODEPROXY = args.mode
    quantity = args.quantity
    num_threads = args.threads

    logger.info("BAT DAU REG")
    tool = UgphoneRegistration()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(tool.register, quantity // num_threads, i) for i in range(num_threads)]
        for future in as_completed(futures):
            future.result()

    logger.info("DONE REG")