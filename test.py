from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import csv
import pandas as pd
import requests
import pytz


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 한국 시간(KST) 타임존 설정
kst = pytz.timezone("Asia/Seoul")

# Load environment variables
load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

# 아이디 리스트 설정
id_list = [
    "terrys_reading",
    "rdnmgo",
    "42lines_",
    "euiclee.books",
    "ai.gi.book",
]


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
    time.sleep(2)  # Wait for the step to proceed
    print("다음 버튼 클릭 완료")


from selenium.webdriver.common.keys import Keys


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
    # div_button = WebDriverWait(driver, 20).until(
    #     EC.element_to_be_clickable(
    #         (
    #             By.XPATH,
    #             '//div[contains(@class, "x1qjc9v5") and contains(@class, "x9f619") and contains(@class, "x78zum5") and @role="button" and @tabindex="0"]',
    #         )
    #     )
    # )
    # div_button.click()
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


def setup_driver():
    print("드라이버 설정 중...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    driver_service = Service(CHROMEDRIVER_PATH)
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


def collect_info(driver, id_list):
    print("정보 수집 시작...")
    data = []
    for user_id in id_list:
        try:
            print(f"{user_id}의 정보 수집 중...")
            driver.get(f"https://www.instagram.com/{user_id}/")
            time.sleep(3)  # 페이지 로드를 위한 대기 시간 증가

            # 게시물 수 추출
            posts_count = driver.find_element(
                By.XPATH, '//*[contains(text(), "게시물")]//span'
            ).text

            # 첫 번째 게시물로 이동
            first_post = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//div[@style="display: flex; flex-direction: column; padding-bottom: 0px; padding-top: 0px; position: relative;"]/div[1]//a',
                    )
                )
            )
            first_post.click()

            time.sleep(3)  # 페이지 로드를 위한 대기 시간 증가

            # "더 보기" 버튼 클릭
            try:
                more_button = driver.find_element(
                    By.XPATH, '//span[contains(text(), "더 보기")]'
                )
                if more_button:
                    more_button.click()
                    time.sleep(2)  # 대기 시간 추가
            except:
                print(f"{user_id}의 게시물에 '더 보기' 버튼 없음")

            # 게시물 텍스트 및 이미지 추출
            post_text = driver.find_element(
                By.CSS_SELECTOR, "div._aagu div._aagv img"
            ).get_attribute("alt")
            post_image = driver.find_element(
                By.CSS_SELECTOR, "div._aagu div._aagv img"
            ).get_attribute("src")
            post_datetime_utc = driver.find_element(
                By.XPATH, '//time[@class="x1p4m5qa"]'
            ).get_attribute("datetime")
            # 게시물 설명 추출
            post_description = driver.find_element(
                By.CSS_SELECTOR, "h1._ap3a._aaco._aacu._aacx._aad7._aade"
            ).text
            # UTC 시간대를 한국 시간대로 변환
            post_datetime_utc = datetime.strptime(
                post_datetime_utc, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            post_datetime_utc = post_datetime_utc.replace(tzinfo=pytz.utc)
            post_datetime_kst = post_datetime_utc.astimezone(kst)

            data.append(
                {
                    "user_id": user_id,
                    "posts_count": posts_count,
                    "post_text": post_text,
                    "post_image": post_image,
                    "post_datetime": post_datetime_kst.strftime("%Y-%m-%d %H:%M:%S"),
                    "post_description": post_description,
                }
            )
            print(f"{user_id}의 정보 수집 완료")
        except Exception as e:
            print(f"{user_id}: 데이터 수집 실패 - {e}")
    print("정보 수집 완료")
    print(data)
    return data


def save_to_csv(data):
    print("CSV 파일에 데이터 저장 중...")
    with open("instagram_data.csv", "w", newline="") as csvfile:
        fieldnames = [
            "user_id",
            "posts_count",
            "post_text",
            "post_image",
            "post_datetime",
            "post_description",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)
    print("CSV 파일에 데이터 저장 완료")


def evaluate_success(data):
    print("성공/실패 평가 중...")
    success_list = []
    failure_list = []
    yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")

    for index, row in data.iterrows():
        post_date = datetime.fromisoformat(row["post_datetime"].split("T")[0])
        if post_date.strftime("%Y-%m-%d") >= yesterday:
            success_list.append(row["user_id"])
        else:
            failure_list.append(row["user_id"])

    print("성공한 사람:", success_list)
    print("실패한 사람:", failure_list)
    return success_list, failure_list


def create_square_image(success_list, failure_list, data):
    print("요약 이미지 생성 중...")
    yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    img_size = 500
    img = Image.new("RGB", (img_size, img_size), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)
    bold_font = ImageFont.truetype(font_path, font_size + 5)
    total_users = len(success_list) + len(failure_list)
    y_text = 20
    d.text(
        (50, y_text),
        f"날짜: {yesterday}",
        font=bold_font,
        fill=(0, 0, 0),
    )
    y_text += 50
    d.text(
        (50, y_text),
        f"성공한 사람 / 전체 사람: {len(success_list)}/{total_users}",
        font=bold_font,
        fill=(0, 0, 0),
    )
    y_text += 50
    d.text((50, y_text), "성공한 사람:", font=font, fill=(0, 0, 0))
    y_text += 20
    for user in success_list:
        upload_time = data[data["user_id"] == user]["post_datetime"].values[0]
        user_info = f"{user} + {upload_time}"
        d.text((50, y_text), user_info, font=font, fill=(0, 128, 0))
        y_text += 20
    y_text += 20  # Add extra space between success and failure lists
    d.text((50, y_text), "실패한 사람:", font=font, fill=(0, 0, 0))
    y_text += 20
    for user in failure_list:
        d.text((50, y_text), user, font=font, fill=(255, 0, 0))
        y_text += 20
    img_path = "result_image.png"
    img.save(img_path)
    print("요약 이미지 생성 완료")
    return img_path


import os
from PIL import Image, ImageDraw, ImageFont
import textwrap


def create_post_images(data, success_list):
    print("포스트 이미지 생성 중...")
    image_paths = []
    output_folder = "output_images"
    os.makedirs(output_folder, exist_ok=True)  # 하위 폴더 생성

    for index, row in data.iterrows():
        if row["user_id"] in success_list:
            user_id = row["user_id"]

            # Create image with post image
            print(f"{user_id}의 이미지 생성 중...")
            img = Image.open(requests.get(row["post_image"], stream=True).raw)
            d = ImageDraw.Draw(img)
            font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
            font_size = 40  # ID가 잘 보이도록 글꼴 크기를 크게 설정
            font = ImageFont.truetype(font_path, font_size)

            # 텍스트 위치 계산
            bbox = d.textbbox((0, 0), user_id, font=font)
            text_width = bbox[2] - bbox[0]
            text_position = (
                (img.width - text_width) / 2,
                img.height * 0.05,
            )  # 이미지 상단 5% 지점에 배치

            # 음영 효과 추가 (흰색 배경)
            shadow_offset = 2
            d.text(
                (text_position[0] + shadow_offset, text_position[1] + shadow_offset),
                user_id,
                font=font,
                fill=(0, 0, 0),
            )
            d.text(
                (text_position[0] - shadow_offset, text_position[1] - shadow_offset),
                user_id,
                font=font,
                fill=(0, 0, 0),
            )
            d.text(
                (text_position[0] + shadow_offset, text_position[1] - shadow_offset),
                user_id,
                font=font,
                fill=(0, 0, 0),
            )
            d.text(
                (text_position[0] - shadow_offset, text_position[1] + shadow_offset),
                user_id,
                font=font,
                fill=(0, 0, 0),
            )

            # 본 텍스트 (검정색)
            d.text(text_position, user_id, font=font, fill=(255, 255, 255))

            img_path = os.path.join(output_folder, f"{user_id}_post_image.png")
            img.save(img_path)
            image_paths.append(img_path)
            print(f"{user_id}의 이미지 생성 완료")

            # Create image with post text
            print(f"{user_id}의 텍스트 이미지 생성 중...")
            text_img = Image.new("RGB", (500, 500), color=(255, 255, 255))
            d = ImageDraw.Draw(text_img)
            font_size = 20
            font = ImageFont.truetype(font_path, font_size)

            # 텍스트 줄바꿈 처리
            max_width = 480  # 텍스트를 그릴 최대 너비
            post_description = str(row["post_description"])  # 문자열로 변환
            lines = textwrap.wrap(
                post_description, width=40
            )  # 적절한 너비로 텍스트를 감쌈

            y_text = 40
            d.text((10, 10), user_id, font=font, fill=(0, 0, 0))  # ID 추가
            for line in lines:
                bbox = d.textbbox((0, 0), line, font=font)
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                d.text(((500 - width) / 2, y_text), line, font=font, fill=(0, 0, 0))
                y_text += height

            text_img_path = os.path.join(output_folder, f"{user_id}_post_text.png")
            text_img.save(text_img_path)
            image_paths.append(text_img_path)
            print(f"{user_id}의 텍스트 이미지 생성 완료")

    print("포스트 이미지 생성 완료")
    return image_paths


def make_description(data):
    description_lines = []

    success_list, failure_list = evaluate_success(data)
    date = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    # 날짜 추가
    description_lines.append(f"날짜: {date}")

    # 성공한 사람 추가
    description_lines.append("성공한 사람:")
    for user in success_list:
        upload_time = data[data["user_id"] == user]["post_datetime"].values[0]
        description_lines.append(f"@{user} (업로드 날짜: {upload_time})")

    # 실패한 사람 추가
    description_lines.append("실패한 사람:")
    for user in failure_list:
        description_lines.append(f"@{user}")

    # 설명

    # 전체 설명을 하나의 문자열로 결합
    description = "\n".join(description_lines) + "\n"

    return description


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
                '//a[contains(@class, "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3")]',
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

    time.sleep(2)  # Wait for the photos to upload
    click_next_buttons(driver)
    click_next_buttons(driver)
    description = make_description(data)
    enter_description(driver, description)
    time.sleep(10)  # Wait for the description to be entered
    share_post(driver)
    print("사진 업로드 완료")


def upload_to_instagram(driver, image_paths, description):
    driver.get("https://www.instagram.com/accounts/login/?next=%2F&source=desktop_nav")
    print("이미지 업로드 시작...")
    time.sleep(2)
    upload_photos(driver, image_paths, description)
    time.sleep(15)  # Wait to ensure the post is shared
    print("이미지 업로드 완료")


def main():
    print("프로그램 시작")
    driver = setup_driver()
    try:
        login_to_instagram(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        # data = collect_info(driver, id_list)
        # save_to_csv(data)
        data = pd.read_csv("instagram_data.csv")
        success_list, failure_list = evaluate_success(data)
        summary_image = create_square_image(success_list, failure_list, data)
        post_images = create_post_images(data, success_list)
        all_images = [summary_image] + post_images
        upload_to_instagram(driver, all_images, data)

    finally:
        driver.quit()
        print("드라이버 종료")


if __name__ == "__main__":
    main()
