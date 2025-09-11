# 🏨 hotel_checker #

</br>

### 남이섬 호텔 예약 감시 자동화 봇 ###

</br>

</br>

### ✨ Features ###

</br>

- Playwright 기반 웹 자동화 / 스크래핑

- 5개 대형 객실(아네모네, 베고니아, 코스모스, 다알리아, 에델바이스) 대상

- 특정 날짜 체크인 가능 여부 자동 감시

- Gmail SMTP 연동 → 예약 가능 시 메일 알림 발송

- Docker 컨테이너로 배포 가능 → 클라우드/서버에서 24시간 상시 실행

- .env 파일로 환경변수 관리 (개인정보/설정 분리)

</br>

### ☁️ Deployment (Optional) ###
- Oracle Cloud Free Tier VM에 Docker 컨테이너로 상시 실행
- Watchtower로 자동 업데이트 지원 (선택)

</br>

### 🛠️ Tech Stack ###
- Python 3.13
- Playwright
- Docker
- Gmail SMTP
- Oracle Cloud Free Tier (Always Free)


</br>

</br>

</br>


### ⚙️ Configuration ###

.env 

```
SMTP_USER=보낼 이메일
SMTP_APP_PASSWORD=앱 비밀번호(공백 없이)
EMAIL_TO=받을 이메일

# 감시 날짜
YEAR=2025
MONTH=10
CHECKIN_DAY=25

# 주기(기본 5~10분 랜덤 대기)
MIN_INTERVAL_SEC=300
MAX_INTERVAL_SEC=600

# 테스트용
HEADLESS=true
```

</br>

### 🚀 How to Run ###

Local
```
pip install playwright python-dotenv
playwright install chromium
python hotel_checker.py
```

Docker
```
docker build -t hotel_checker .
docker run -d --name hotel --env-file .env hotel_checker
```

</br>

</br>

### 유용한 팁 정리 ###

</br>

- 로그 보기 시작/종료

```
sudo docker logs -f hotel      # 실시간 추적 (종료: Ctrl+C)
sudo docker logs --since=1h hotel   # 최근 1시간만 확인
```

</br>

- 상태/재시작/중지

```
sudo docker ps
sudo docker restart hotel
sudo docker stop hotel
sudo docker start hotel
```

</br>

- 환경값 바꿨을 때(예: 날짜 변경) 다시 띄우기

```nano prod.env        # 값 수정 저장
sudo docker stop hotel && sudo docker rm hotel
sudo docker run -d --name hotel --restart unless-stopped \
  --env-file prod.env ghcr.io/1116cafemocha/hotel_checker:latest
```

</br>

- 업데이트 자동 반영(선택)
  - 5분마다 새 이미지 확인 → 있으면 자동 pull + 재시작
  - --cleanup으로 오래된 이미지 정리
```
sudo docker run -d --name watchtower --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower hotel \
  --interval 300 --cleanup --include-restarting --revive-stopped
```

</br>

- OCI에서 최신으로 다시 받기 & 검증
```
# 서버(ubuntu@…):
# 컨테이너 중지/삭제
sudo docker stop hotel || true
sudo docker rm hotel || true

# 로컬 캐시 이미지 삭제 (강제로 최신 받기)
sudo docker rmi ghcr.io/1116cafemocha/hotel_checker:latest || true

# 최신 pull
sudo docker pull ghcr.io/1116cafemocha/hotel_checker:latest
```

</br>

- 모듈 존재 여부 확인
```
# playwright 있어야 True
sudo docker run --rm ghcr.io/1116cafemocha/hotel_checker:latest \
  python -c "import importlib.util; print(importlib.util.find_spec('playwright') is not None)"

# dotenv 있어야 True
sudo docker run --rm ghcr.io/1116cafemocha/hotel_checker:latest \
  python -c "import importlib.util; print(importlib.util.find_spec('dotenv') is not None)"
```

</br>

- 컨테이너 실행
```
sudo docker run -d --name hotel --restart unless-stopped \
  --env-file prod.env \
  ghcr.io/1116cafemocha/hotel_checker:latest

sudo docker logs -f hotel
```
