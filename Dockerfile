FROM        pignu/eb_weathersound
MAINTAINER  hanyul.ryu@gmail.com

ENV         LANG C.UTF-8

# 컨테이너 내 복사
COPY        . /srv/weathersound
# cd /srv/deploy_eb/docker 와 같음
WORKDIR     /srv/weathersound

# requiremments.txt 설치
RUN         /root/.pyenv/versions/weathersound/bin/pip install -r .requirements/deploy.txt

# .config/supervisor/uwsgi.conf로 이동
#RUN         uwsgi --http :8000 --chdir /srv/deploy_ec2/django_app --home /root/.pyenv/versions/deploy_eb_docker -w config.settings.debug

# supervisor 파일 복사
COPY        .config/supervisor/uwsgi.conf /etc/supervisor/conf.d/
COPY        .config/supervisor/nginx.conf /etc/supervisor/conf.d/


# nginx 설정파일, nginx 사이트 파일 복사
COPY        .config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY        .config/nginx/nginx-app.conf /etc/nginx/sites-available/nginx-app.conf

# nginx 링크 작성
RUN         rm -rf /etc/nginx/sites-enabled/default
RUN         ln -sf /etc/nginx/sites-available/nginx-app.conf /etc/nginx/sites-enabled/nginx.conf

# collectstatic 실행
RUN         /root/.pyenv/versions/weathersound/bin/python /srv/weathersound/django_app/manage.py collectstatic --settings=config.settings.deploy --noinput

# front프로젝트 복사
WORKDIR     /srv
RUN         git clone -b beomdu https://github.com/dlqjaen/WeatherSound.git front
WORKDIR     /srv/front/weather_sound_project/
RUN         npm install
RUN         npm run build

CMD         supervisord -n
# 80포트와 8000포트를 열어줌
EXPOSE      80 8000 8080
