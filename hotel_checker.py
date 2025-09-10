# 남이섬 호텔정관루(아네모네/베고니아/코스모스/다알리아/에델바이스) 빈 방 확인용 코드! (예약 및 결제는 x)
# 특정 날짜(체크인 기준) 예약 가능 시 Gmail로 알림!
# 현재 목표 : 10월 25일 체크인

import sys, os, asyncio, re, random, time, ssl, smtplib
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
load_dotenv()  # .env 파일 자동 로드

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ──[환경변수]────────────────────────────────────────────────────────────
SMTP_USER = os.environ["SMTP_USER"]                  # 발신 Gmail
SMTP_APP_PASSWORD = os.environ["SMTP_APP_PASSWORD"]  # 앱 비밀번호(16자, 공백 제거)
EMAIL_TO = os.environ["EMAIL_TO"]                    # 수신 주소

# 감시 날짜(기본값: 2025-10-25 체크인) — 필요하면 컨테이너 실행 시 오버라이드 가능
YEAR = int(os.getenv("YEAR", "2025"))
MONTH = int(os.getenv("MONTH", "10"))
CHECKIN_DAY = int(os.getenv("CHECKIN_DAY", "25"))

# 주기(기본 5~10분 랜덤 대기)
MIN_INTERVAL_SEC = int(os.getenv("MIN_INTERVAL_SEC", "300"))   # 5분
MAX_INTERVAL_SEC = int(os.getenv("MAX_INTERVAL_SEC", "600"))   # 10분

PAGE_TIMEOUT_MS = int(os.getenv("PAGE_TIMEOUT_MS", "60000"))
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")

# ──[대상 객실]────────────────────────────────────────────────────────────
ROOMS = {
    "아네모네": 34,
    "베고니아": 60,
    "코스모스": 61,
    "다알리아": 62,
    "에델바이스": 63,
}
STATE_FILE = Path("nami_state.txt")  # 마지막 발송 메시지 저장(중복알림 방지)

# ──────────────────────────────────────────────────────────────────────────
PRICE_RE = re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d{4,})\s*원?")

def send_email(subject: str, body: str):
    """Gmail SMTP로 메일 발송"""
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    ctx = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
        s.starttls(context=ctx)
        s.login(SMTP_USER, SMTP_APP_PASSWORD)
        s.sendmail(SMTP_USER, [EMAIL_TO], msg.as_string())

def read_state() -> str:
    return STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else ""

def write_state(s: str):
    STATE_FILE.write_text(s, encoding="utf-8")

def looks_like_price(text: str) -> bool:
    return bool(PRICE_RE.search(text))

async def get_day_text(page, day: int) -> str:
    """날짜 숫자 주변 컨테이너 단위로 텍스트를 가져와 '예약불가' 또는 '가격' 문구를 함께 읽어옴."""
    candidates = [
        f"//*[normalize-space(text())='{day}']",
        f"//button[normalize-space(.)='{day}']",
    ]
    for xp in candidates:
        loc = page.locator(f"xpath={xp}")
        if await loc.count() == 0:
            continue
        container = loc.first.locator(
            "xpath=ancestor-or-self::*[self::li or self::div or self::button][1]"
        )
        try:
            txt = (await container.inner_text()).strip()
            if txt:
                return txt
        except:
            pass
    return ""

async def check_one_room(p, ho_idx: int, headless=True) -> bool:
    """한 객실의 지정 월 달력에서 CHECKIN_DAY 가격 표기가 보이면 '가능'."""
    url = f"https://naminara.net/main/page/hotel_detail.php?ho_idx={ho_idx}&syear={YEAR}&smonth={MONTH}"
    browser = await p.chromium.launch(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    ctx = await browser.new_context(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"),
        locale="ko-KR",
        timezone_id="Asia/Seoul",
    )
    page = await ctx.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        try:
            await page.wait_for_load_state("networkidle", timeout=8000)
        except:
            pass

        # 달력 모달 수동 오픈 필요 시 대비
        try:
            btn = page.locator("button:has-text('날짜'), button:has-text('선택')")
            if await btn.count() > 0:
                await btn.first.click(timeout=1500)
        except:
            pass

        t_in = await get_day_text(page, CHECKIN_DAY)
        ok_in = ("예약불가" not in t_in) and looks_like_price(t_in)
        return ok_in

    finally:
        await ctx.close()
        await browser.close()

async def main_loop():
    last_msg = read_state()
    async with async_playwright() as p:
        while True:
            available = []
            for name, idx in ROOMS.items():
                try:
                    ok = await check_one_room(p, idx, headless=HEADLESS)
                except Exception as e:
                    ok = False
                    print(f"[에러] {name}({idx}): {e}")
                print(f"- {name}: {'가능' if ok else '불가'}")
                if ok:
                    available.append(name)

            if available:
                lines = [
                    f"[남이섬 호텔정관루] {YEAR}-{MONTH:02d}-{CHECKIN_DAY} 체크인 기준 예약 가능 감지!",
                    f"객실: {', '.join(available)}",
                    "",
                ]
                for r in available:
                    url = f"https://naminara.net/main/page/hotel_detail.php?ho_idx={ROOMS[r]}&syear={YEAR}&smonth={MONTH}"
                    lines.append(f"- {r}: {url}")
                msg = "\n".join(lines)

                if msg != last_msg:
                    send_email("호텔정관루 예약 가능!", msg)
                    write_state(msg)
                    last_msg = msg
                    print("[메일 발송] 가능 객실 발견 → 알림 전송")
                else:
                    print("[스킵] 동일 내용은 이미 알림 발송됨")
            else:
                print("현재는 모든 대상 방이 불가")

            sleep_sec = random.randint(MIN_INTERVAL_SEC, MAX_INTERVAL_SEC)
            print(f"다음 확인까지 {sleep_sec}초 대기...\n")
            time.sleep(sleep_sec)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("중지합니다.")
