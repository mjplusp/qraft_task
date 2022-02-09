FROM python:3.8.10
ENV PYTHONUNBUFFERED=1
# Docker의 python버전을 설정

RUN apt-get -y update
RUN apt-get -y install vim
RUN pip install --upgrade pip
# docker안에서 srv/docker-server 폴더 생성
# 작업 디렉토리 설정
RUN mkdir -p /srv/docker-server/logs
RUN mkdir -p /srv/docker-server/database
WORKDIR /srv/docker-server

# pip 업그레이드 / 필수 패키지 설치
COPY qraft/requirements.txt  requirements.txt
RUN pip install -r requirements.txt

# ADD . /srv/docker-server
# 현재 디렉토리를 통째로 srv/docker-server 폴더에 복사
COPY qraft/qraft qraft
COPY qraft/qraft_users qraft_users
COPY qraft/manage.py  manage.py
COPY entrypoint.sh entrypoint.sh
# COPY selfsigned.key  selfsigned.key
# COPY selfsigned.crt  selfsigned.crt

RUN python manage.py migrate

EXPOSE 8000
ENTRYPOINT [ "/bin/bash", "/srv/docker-server/entrypoint.sh" ]