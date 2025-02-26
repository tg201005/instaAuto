import os
import pandas as pd
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, CHROMEDRIVER_PATH, id_list
from instagram import setup_driver, login_to_instagram, upload_to_instagram
from data_processing import (
    evaluate_success,
    save_to_csv,
    collect_info_learning_machine,
    get_following_list,
)
from image_processing import create_square_image, create_post_images


# 1.leanring_machine.py
def main():
    print("프로그램 시작")
    driver = setup_driver(CHROMEDRIVER_PATH)
    try:
        login_to_instagram(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        data = collect_info_learning_machine(driver, id_list)
        save_to_csv(data, "instagram_data.csv")
        data = pd.read_csv("instagram_data.csv")
        success_list, failure_list = evaluate_success(data)
        summary_image = create_square_image(success_list, failure_list, data)
        post_images = create_post_images(data, success_list)
        all_images = [summary_image] + post_images
        upload_to_instagram(driver, all_images, data)
    finally:
        driver.quit()
        print("드라이버 종료")


# # 2. get following list


# def main():
#     print("프로그램 시작")
#     driver = setup_driver(CHROMEDRIVER_PATH)
#     try:
#         login_to_instagram(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
#         # data = get_following_list(driver, id_list)
#         data = get_following_list(driver, ["yusinae_book"])
#         save_to_csv(data, "instagram_data.csv")

#     finally:
#         driver.quit()
#         print("드라이버 종료")


# if __name__ == "__main__":
#     main()
