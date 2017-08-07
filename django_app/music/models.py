# from forecastiopy import *

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

__all__ = (
    'Music',
    'Weather',
    'Playlist',
    'PlaylistMusics',
)

User = get_user_model()


# 전체 음악파일/정보 모델
class Music(models.Model):
    # album image 저장용
    # TODO artist || nameMusic으로 index생성 고려
    # img_music = models.ImageField(upload_to='img_music', blank=True)
    img_music = models.CharField(
        max_length=256,
        null=False,
        blank=False,
    )
    # file_music = models.FileField(upload_to='music')
    time_music = models.PositiveSmallIntegerField(
        default=0,
    )
    source_music = models.CharField(  # 음악 파일 저장된 위치 주소 리턴
        max_length=256,
        null=False,
        blank=False,
        # unique=True,
    )
    name_music = models.CharField(
        max_length=100,
    )
    name_artist = models.CharField(
        max_length=100,
    )
    name_album = models.CharField(
        max_length=100,
        blank=True,
    )
    sunny = models.PositiveIntegerField(
        verbose_name='맑음', default=0)
    foggy = models.PositiveIntegerField(
        verbose_name='안개', default=0)
    rainy = models.PositiveIntegerField(
        verbose_name='비', default=0)
    cloudy = models.PositiveIntegerField(
        verbose_name='흐림', default=0)
    snowy = models.PositiveIntegerField(
        verbose_name='눈', default=0)

    def __str__(self):
        return self.name_music


# TODO 잘못된 좌표가 들어왓을 떄의 처리
class WeatherManager(models.Manager):
    """
    Weather용 manager
        _get_location_info : 좌표를 받아서 지명으로 변환
        _get_weather_info  : 좌표르 받아서 날씨 정보 반환
        create_or_update_weather :  좌표를 입력받아서 지명을 uniqueKey로 하는 Weather class 생성
                                    만약 이미 같은 지명의 객체가 존재하면 시간과 날씨를 업데이트
    """
    weather_dict = {
        "clear-day": "sunny",
        "clear-night": "sunny",
        "partly-cloudy-day": "sunny",
        "partly-cloudy-night": "sunny",
        "rain": "rainy",
        "snow": "snowy",
        "wind": "sunny",
        "sleet": "foggy",
        "fog": "foggy",
        "cloudy": "cloudy",

    }

    # a = [37.497799, 127.027482] # test 좌표
    def _get_location_info(self, latitude, longitude):
        url = "https://maps.googleapis.com/maps/api/geocode/json" \
              "?latlng={LATITUDE},{LONGITUDE}" \
              "&key={SECRET_KEY}" \
              "&language=ko" \
              "&result_type={result_type}".format(LATITUDE=latitude,
                                                  LONGITUDE=longitude,
                                                  SECRET_KEY=settings.GOOGLE_API_KEY,
                                                  result_type="sublocality", )

        return requests.get(url).json()["results"][2]["formatted_address"]

    def _get_weather_info(self, latitude, longitude):
        url = "https://api.darksky.net/forecast/" \
              "{SECRET_KEY}/" \
              "{LATITUDE},{LONGITUDE}".format(SECRET_KEY=settings.DARKSKY_API_KEY,
                                              LATITUDE=latitude,
                                              LONGITUDE=longitude, )
        data = requests.get(url=url).json()
        current_weather = self.weather_dict[data["currently"]["icon"]]
        temperature = data["currently"]["temperature"]
        return current_weather, temperature

    def create_or_update_weather(self, latitude, longitude):
        addr = self._get_location_info(latitude, longitude)
        current_weather, temperature = self._get_weather_info(latitude, longitude)
        weather, weather_created = self.get_or_create(
            location=addr,
            defaults={
                "current_weather": current_weather,
                "temperature": temperature,
            }
        )

        if not weather_created and (timezone.now() - weather.time_saved).seconds >= 3600:
            weather.current_weather = current_weather
            weather.temperature = temperature
            weather.time_saved = timezone.now()
            weather.save()


class Weather(models.Model):
    objects = WeatherManager()
    location = models.CharField(  # 지명 ex) 서울시 서초구 반포동
        max_length=100,
        unique=True,
    )
    current_weather = models.CharField(  # 지금의 날씨 (미리 분류된 5가지)
        max_length=10,
    )
    time_saved = models.DateTimeField(  # 저장된 시간
        auto_now=True,
        # editable=True,
    )
    temperature = models.FloatField(  # 지금 온도
        default=18.0,
    )


# 유저별 플레이리스트 모델
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name_playlist = models.CharField(max_length=30, default='playlist')
    playlist_musics = models.ManyToManyField(
        'Music',
        through='PlaylistMusics',
        related_name='playlist_musics'
    )

    def __str__(self):
        return '{}의 {}'.format(
            self.user,
            self.name_playlist)


# 유저의 플레이리스트 내 음악 목록 모델
class PlaylistMusics(models.Model):
    name_playlist = models.ForeignKey('Playlist', on_delete=models.CASCADE)
    music = models.ForeignKey('Music', on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '리스트 {}의 음악 {}'.format(
            self.name_playlist,
            self.music
        )
