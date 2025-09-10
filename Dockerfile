FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy
WORKDIR /app

# python-dotenv 설치 (playwright는 베이스 이미지에 이미 포함)
RUN pip install --no-cache-dir python-dotenv

# 소스 복사 (requirements 불필요: 베이스 이미지에 playwright/브라우저 포함)
COPY hotel_checker.py /app/hotel_checker.py

ENV PYTHONUNBUFFERED=1 TZ=Asia/Seoul
CMD ["python", "/app/hotel_checker.py"]