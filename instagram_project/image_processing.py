from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap
import os
from datetime import datetime, timedelta

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
    d.text((50, y_text), f"날짜: {yesterday}", font=bold_font, fill=(0, 0, 0))
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
    y_text += 20
    d.text((50, y_text), "실패한 사람:", font=font, fill=(0, 0, 0))
    y_text += 20
    for user in failure_list:
        d.text((50, y_text), user, font=font, fill=(255, 0, 0))
        y_text += 20
    img_path = "result_image.png"
    img.save(img_path)
    print("요약 이미지 생성 완료")
    return img_path

def create_post_images(data, success_list):
    print("포스트 이미지 생성 중...")
    image_paths = []
    output_folder = "output_images"
    os.makedirs(output_folder, exist_ok=True)

    for index, row in data.iterrows():
        if row["user_id"] in success_list:
            user_id = row["user_id"]

            print(f"{user_id}의 이미지 생성 중...")
            img = Image.open(requests.get(row["post_image"], stream=True).raw)
            d = ImageDraw.Draw(img)
            font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
            font_size = 40
            font = ImageFont.truetype(font_path, font_size)

            bbox = d.textbbox((0, 0), user_id, font=font)
            text_width = bbox[2] - bbox[0]
            text_position = (
                (img.width - text_width) / 2,
                img.height * 0.05,
            )

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

            d.text(text_position, user_id, font=font, fill=(255, 255, 255))

            img_path = os.path.join(output_folder, f"{user_id}_post_image.png")
            img.save(img_path)
            image_paths.append(img_path)
            print(f"{user_id}의 이미지 생성 완료")

            print(f"{user_id}의 텍스트 이미지 생성 중...")
            text_img = Image.new("RGB", (500, 500), color=(255, 255, 255))
            d = ImageDraw.Draw(text_img)
            font_size = 20
            font = ImageFont.truetype(font_path, font_size)

            max_width = 480
            post_description = str(row["post_description"])
            lines = textwrap.wrap(post_description, width=40)

            y_text = 40
            d.text((10, 10), user_id, font=font, fill=(0, 0, 0))
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
