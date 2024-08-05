import pandas as pd
from datetime import datetime, timedelta
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytz
import openai
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

kst = pytz.timezone("Asia/Seoul")

import openai
import os

# Load the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


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


def like_post(driver):
    try:
        # "좋아요" 버튼 찾기
        like_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//svg[@aria-label="좋아요"]'))
        )
        if like_button:
            like_button.click()
            print("좋아요 버튼을 클릭했습니다.")
    except:
        print("좋아요 버튼이 없습니다. 이미 좋아요를 눌렀거나 오류가 발생했습니다.")

    try:
        # "좋아요 취소" 버튼 찾기
        unlike_button = driver.find_element(
            By.XPATH, '//svg[@aria-label="좋아요 취소"]'
        )
        if unlike_button:
            print("이미 좋아요를 누른 상태입니다. 아무 동작도 하지 않습니다.")
    except:
        print("좋아요 취소 버튼이 없습니다.")


def save_to_csv(data, filename):
    print("CSV 파일에 데이터 저장 중...")
    with open(filename, "w", newline="") as csvfile:
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


def make_description(data):
    description_lines = []

    success_list, failure_list = evaluate_success(data)
    date = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    description_lines.append(f"날짜: {date}")
    description_lines.append("성공한 사람:")
    for user in success_list:
        upload_time = data[data["user_id"] == user]["post_datetime"].values[0]
        description_lines.append(f"@{user} (업로드 날짜: {upload_time})")

    description_lines.append("실패한 사람:")
    for user in failure_list:
        description_lines.append(f"@{user}")

    description = "\n".join(description_lines) + "\n"

    return description


def generate_comment(post_description):
    print("Generating comment for the post description...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"다음 설명에 어울리는 인스타그램 댓글을 작성하라. 문장은 완결체로 종결하라.: {post_description}",
        },
    ]

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, max_tokens=150
            )
            comment = response.choices[0].message["content"].strip()
            print(f"Generated comment: {comment}")
            return comment
        except Exception as e:
            print(f"Error generating comment: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)


def post_comment(driver, comment):
    print("Posting comment...")
    comment_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "textarea.x1i0vuye.xvbhtw8.x1ejq31n")
        )
    )
    comment_box.click()
    comment_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "textarea.x1i0vuye.xvbhtw8.x1ejq31n")
        )
    )
    comment_box.send_keys(comment)
    comment_box.send_keys(Keys.RETURN)
    print(f"Comment to post: {comment}")

    time.sleep(2)  # Wait for the comment to be posted
    print("Comment posted successfully")


def get_user_posts_count(driver):
    posts_count = driver.find_element(
        By.XPATH, '//*[contains(text(), "게시물")]//span'
    ).text
    return posts_count


def get_first_post(driver):
    first_post = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//div[@style="display: flex; flex-direction: column; padding-bottom: 0px; padding-top: 0px; position: relative;"]/div[1]//a',
            )
        )
    )
    first_post.click()
    time.sleep(3)


def click_more_button(driver, user_id):
    try:
        more_button = driver.find_element(
            By.XPATH, '//span[contains(text(), "더 보기")]'
        )
        if more_button:
            more_button.click()
            time.sleep(2)
    except:
        print(f"{user_id}의 게시물에 '더 보기' 버튼 없음")


def collect_post_info(driver):
    post_text = driver.find_element(
        By.CSS_SELECTOR, "div._aagu div._aagv img"
    ).get_attribute("alt")
    post_image = driver.find_element(
        By.CSS_SELECTOR, "div._aagu div._aagv img"
    ).get_attribute("src")
    post_datetime_utc = driver.find_element(
        By.XPATH, '//time[@class="x1p4m5qa"]'
    ).get_attribute("datetime")
    post_description = driver.find_element(
        By.CSS_SELECTOR, "h1._ap3a._aaco._aacu._aacx._aad7._aade"
    ).text
    post_datetime_utc = datetime.strptime(post_datetime_utc, "%Y-%m-%dT%H:%M:%S.%fZ")
    post_datetime_utc = post_datetime_utc.replace(tzinfo=pytz.utc)
    post_datetime_kst = post_datetime_utc.astimezone(kst)

    return post_text, post_image, post_datetime_kst, post_description


def collect_info_learning_machine(driver, id_list):
    print("정보 수집 시작...")
    data = []
    for user_id in id_list:
        try:
            print(f"{user_id}의 정보 수집 중...")
            driver.get(f"https://www.instagram.com/{user_id}/")
            time.sleep(3)

            posts_count = get_user_posts_count(driver)
            get_first_post(driver)

            click_more_button(driver, user_id)
            post_text, post_image, post_datetime_kst, post_description = (
                collect_post_info(driver)
            )
            like_post(driver)
            # post_comment(driver, generate_comment(post_description))
            post_comment(driver, "오늘 하루도 학습하느라 고생하셨어요!!")

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
    return data


############################################################################################################


def click_followers_link(driver):
    try:
        followers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "팔로워")]'))
        )
        followers_link.click()
        print("팔로워 링크를 클릭했습니다.")

    except Exception as e:
        print(f"팔로워 링크를 클릭하는데 실패했습니다: {e}")


def click_following_link(driver):
    try:
        following_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="/terrys_reading/following/"]')
            )
        )
        following_link.click()
        print("팔로우 링크를 클릭했습니다.")
    except Exception as e:
        print(f"팔로우 링크를 클릭하는데 실패했습니다: {e}")


def scroll_until_recommended(driver):
    # 다이어로그 셀렉터를 통해 요소를 찾기
    time.sleep(3)
    dialog_selector = "body > div.x1n2onr6.xzkaem6 > div:nth-child(2) > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div"
    dialog = driver.find_element(By.CSS_SELECTOR, dialog_selector)

    # 지속적으로 스크롤하며 "회원님을 위한 추천" 요소를 찾기
    while True:
        # # JavaScript를 사용하여 다이어로그 요소를 스크롤
        # dialog = driver.find_element(
        #     By.CSS_SELECTOR,
        #     "div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1iyjqo2.x2lwn1j.xeuugli.xdt5ytf.xqjyukv.x1cy8zhl.x1oa3qoh.x1nhvcw1",
        # )
        # scroll_script = """arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;"""
        # driver.execute_script(scroll_script, dialog)

        ActionChains(driver).drag_and_drop_by_offset(dialog, 0, 100).perform()

        # 잠시 대기
        time.sleep(1)

        try:
            # "회원님을 위한 추천" 요소를 찾기
            recommended_element = driver.find_element(
                By.XPATH, '//span[text()="회원님을 위한 추천"]'
            )
            if recommended_element:
                print("추천 요소 발견!")
                break
        except:
            continue

    # id와 설명을 추출
    items = driver.find_elements(
        By.CSS_SELECTOR,
        "div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1iyjqo2.x2lwn1j.xeuugli.xdt5ytf.xqjyukv.x1cy8zhl.x1oa3qoh.x1nhvcw1",
    )
    for item in items:
        try:
            id_element = item.find_element(By.CSS_SELECTOR, "a > div > div > span")
            description_element = item.find_element(By.CSS_SELECTOR, 'span[dir="auto"]')
            print(f"ID: {id_element.text}, Description: {description_element.text}")
        except:
            continue


def get_following_list(driver, id_list):
    print("정보 수집 시작...")
    data = []
    for user_id in id_list:
        try:
            print(f"{user_id}의 정보 수집 중...")
            driver.get(f"https://www.instagram.com/{user_id}/")
            time.sleep(3)
            click_followers_link(driver)

            # 팔로워 팝업 로드 대기
            followers_popup = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//div[contains(@class, "xyi19xy") and contains(@class, "x1ccrb07")]',
                    )
                )
            )
            print("팔로워 팝업이 로드되었습니다.")

            # # 팔로워 팝업 스크롤
            # scroll_script = "arguments[0].scrollTop = arguments[0].scrollHeight;"
            # while True:
            #     last_count = len(
            #         WebDriverWait(driver, 10).until(
            #             EC.presence_of_all_elements_located(
            #                 (
            #                     By.XPATH,
            #                     '//div[@class="xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6"]//li',
            #                 )
            #             )
            #         )
            #     )
            #     driver.execute_script(scroll_script, followers_popup)
            #     time.sleep(1)  # 팔로워 로드 대기
            #     new_count = len(
            #         WebDriverWait(driver, 10).until(
            #             EC.presence_of_all_elements_located(
            #                 (
            #                     By.XPATH,
            #                     '//div[@class="xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6"]//li',
            #                 )
            #             )
            #         )
            #     )
            #     if new_count == last_count:
            #         break  # 새로운 팔로워가 로드되지 않으면 루프 종료
            scroll_until_recommended(driver)
            print("모든 팔로워를 로드했습니다.")

        except Exception as e:
            print(f"{user_id}: 데이터 수집 실패 - {e}")

    return data
