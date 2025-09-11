FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy
WORKDIR /app

# 필요한 파이썬 패키지 설치
# - playwright: 파이썬 바인딩
# - python-dotenv: .env 로딩
RUN pip install --no-cache-dir "playwright==1.46.*" python-dotenv

# (안전) 브라우저 설치 – 베이스에 이미 있을 가능성이 높지만, 없을 때 대비
RUN playwright install chromium

# 소스 복사 (requirements 불필요: 베이스 이미지에 playwright/브라우저 포함)
COPY hotel_checker.py /app/hotel_checker.py

ENV PYTHONUNBUFFERED=1 TZ=Asia/Seoul
CMD ["python", "/app/hotel_checker.py"]