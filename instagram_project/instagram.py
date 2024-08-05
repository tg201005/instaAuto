from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import os
from datetime import datetime, timedelta
from data_processing import evaluate_success, make_description


def setup_driver(chromedriver_path):
    print("드라이버 설정 중...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    driver_service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    print("드라이버 설정 완료")
    return driver


def login_to_instagram(driver, username, password):
    print("인스타그램 로그인 시도 중...")
    driver.get("https://www.instagram.com/accounts/login/?next=%2F&source=desktop_nav")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    print("로그인 정보 입력 완료")
    click_save_info_button(driver)


def click_save_info_button(driver):
    print("로그인 정보 저장 버튼 클릭 중...")
    save_info_button = WebDriverWait(driver, 200).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button._acan._acap._acas._aj1-._ap30")
        )
    )
    save_info_button.click()
    print("로그인 정보 저장 버튼 클릭 완료")


def click_next_buttons(driver):
    print("다음 버튼 클릭 중...")
    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//div[@role="button" and text()="다음"]')
        )
    )
    driver.execute_script("arguments[0].click();", next_button)
    time.sleep(2)
    print("다음 버튼 클릭 완료")


def enter_description(driver, description):
    print("설명 입력 중...")
    description_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@aria-label="문구를 입력하세요..."]')
        )
    )
    description_box.click()
    description_box.send_keys(description)
    description_box.send_keys(Keys.RETURN)
    description_box.click()
    print("설명 입력 완료")


def share_post(driver):
    print("게시물 공유 중...")
    share_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//div[@role="button" and text()="공유하기"]')
        )
    )
    driver.execute_script("arguments[0].click();", share_button)
    print("게시물 공유 완료")


def upload_photos(driver, image_paths, data):
    print("사진 업로드 중...")
    new_post_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="새로운 게시물"]'))
    )
    new_post_button.click()

    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//a[contains(@class, "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3")]',
            )
        )
    )
    element.click()

    print("새 게시물 버튼 클릭 완료")
    file_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    absolute_image_paths = [os.path.abspath(path) for path in image_paths]
    file_input.send_keys("\n".join(absolute_image_paths))

    time.sleep(2)
    click_next_buttons(driver)
    click_next_buttons(driver)
    description = make_description(data)
    enter_description(driver, description)
    time.sleep(10)
    share_post(driver)
    print("사진 업로드 완료")


def upload_to_instagram(driver, image_paths, description):
    driver.get("https://www.instagram.com/accounts/login/?next=%2F&source=desktop_nav")
    print("이미지 업로드 시작...")
    time.sleep(2)
    upload_photos(driver, image_paths, description)
    time.sleep(15)
    print("이미지 업로드 완료")
