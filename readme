# 인스타그램 자동화 스크립트

이 스크립트는 인스타그램 계정에서 정보를 수집하고, 최근 활동을 기반으로 성공 여부를 평가하며, 요약 이미지를 생성하고 설명과 함께 인스타그램에 업로드하는 과정을 자동화합니다.

## 요구사항

- Python 3.7 이상
- 필요한 Python 패키지:
  - `selenium`
  - `pillow`
  - `python-dotenv`
  - `pandas`
  - `requests`
  - `pytz`

다음 명령어를 사용하여 필요한 패키지를 설치할 수 있습니다:
```sh
pip install selenium pillow python-dotenv pandas requests pytz
```

## 설정

1. **환경 변수 설정**:
   프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가합니다:
   ```env
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   CHROMEDRIVER_PATH=path_to_chromedriver
   ```

2. **인스타그램 사용자 ID 목록**:
   스크립트 내의 `id_list` 변수에 추적하고 싶은 인스타그램 사용자 ID를 추가합니다.

3. **ChromeDriver**:
   ChromeDriver가 설치되어 있고, 해당 경로가 `.env` 파일에 올바르게 설정되어 있는지 확인합니다. ChromeDriver는 [여기](https://sites.google.com/a/chromium.org/chromedriver/downloads)에서 다운로드할 수 있습니다.

## 실행 방법

1. **스크립트 실행**:
   Python을 사용하여 스크립트를 실행합니다:
   ```sh
   python script_name.py
   ```

## 함수 설명

### 1. `click_save_info_button(driver)`
로그인 후 "정보 저장" 버튼을 클릭합니다.

### 2. `click_next_buttons(driver)`
게시물 업로드 과정에서 "다음" 버튼을 클릭합니다.

### 3. `enter_description(driver, description)`
인스타그램 게시물에 설명을 입력합니다.

### 4. `share_post(driver)`
"공유" 버튼을 클릭하여 게시물을 업로드합니다.

### 5. `setup_driver()`
Chrome 옵션을 설정하여 Selenium WebDriver를 설정합니다.

### 6. `login_to_instagram(driver, username, password)`
주어진 사용자 이름과 비밀번호를 사용하여 인스타그램에 로그인합니다.

### 7. `collect_info(driver, id_list)`
지정된 인스타그램 사용자 ID 목록에서 정보를 수집합니다. 게시물 수, 텍스트, 이미지 URL, 설명을 가져오며, 게시물의 날짜와 시간을 KST (한국 표준시)로 변환합니다.

### 8. `save_to_csv(data)`
수집된 데이터를 CSV 파일로 저장합니다.

### 9. `evaluate_success(data)`
최근 활동을 기반으로 사용자의 성공 여부를 평가합니다.

### 10. `create_square_image(success_list, failure_list, data)`
성공 및 실패 목록을 표시하는 요약 이미지를 생성합니다.

### 11. `create_post_images(data, success_list)`
각 성공한 사용자의 게시물에 사용자 ID를 상단에 표시하여 이미지를 생성합니다.

### 12. `make_description(data)`
날짜, 성공한 사용자(업로드 날짜 포함), 실패한 사용자 목록을 포함한 인스타그램 게시물 설명을 생성합니다.

### 13. `upload_photos(driver, image_paths, data)`
생성된 이미지를 설명과 함께 인스타그램에 업로드합니다.

### 14. `upload_to_instagram(driver, image_paths, description)`
인스타그램에 로그인하고 이미지를 업로드하는 전체 과정을 처리합니다.

### 15. `main()`
전체 스크립트를 실행하는 메인 함수입니다.

## 예제

```python
if __name__ == "__main__":
    main()
```

이 스크립트는 인스타그램에 로그인하고, 필요한 데이터를 수집하고, 사용자의 성공 여부를 평가하고, 필요한 이미지를 생성하고, 상세 설명과 함께 인스타그램에 업로드합니다.

## 주의사항

- 인스타그램 계정이 2단계 인증으로 보호되지 않았는지 확인하거나, 추가 인증 단계를 처리하도록 스크립트를 조정하세요.
- 인스타그램의 사용 제한 및 API 사용 정책을 준수하여 계정이 차단되지 않도록 주의하세요.
```
