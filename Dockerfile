# 3.9 version
FROM python:3.9.17-slim

# work dir 변경
WORKDIR /app

# 패키지 설치
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# 스크립트 복사
COPY bot.py bot.py

# 실행
CMD [ "python3", "bot.py" ]