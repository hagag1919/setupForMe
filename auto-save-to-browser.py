from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


options = webdriver.EdgeOptions()
# Open the browser Edge
browser = webdriver.Edge(
    options=options
)
browser.get('edge://wallet/passwords?source=assetsSettingsPassword')
time.sleep(40)
# Find the add password field
add_password = browser.find_element(By.ID, 'add-password')
add_password.click()
time.sleep(2)
# Find the url field
url = browser.find_element(By.ID, 'field-105__control')
url.send_keys('https://example.com')
# Find the username field
username = browser.find_element(By.ID, 'field-106__control')
username.send_keys('username')
# Find the password field
password = browser.find_element(By.ID, 'field-107__control')
password.send_keys('password')
# Find the save button
save_button = browser.find_element(By.ID, 'save')
save_button.click()
time.sleep(2)
browser.quit()

