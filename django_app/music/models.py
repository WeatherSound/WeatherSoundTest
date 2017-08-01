import os
# from forecastiopy import *
import requests
import config
from django.contrib.auth import get_user_model
from django.db import models


__all__ = (
    'Music',
    'Weather',
    'Playlist',
    'PlaylistMusics',
)

User = get_user_model()


# 전체 음악파일/정보 모델
class Music(models.Model):
    name_author = models.ForeignKey(User, on_delete=models.CASCADE)
    img_music = models.ImageField(upload_to='img_music', blank=True)
    name_music = models.CharField(max_length=100)
    name_singer = models.CharField(max_length=100)
    file_music = models.FileField(upload_to='music')
    name_album = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    sunny = models.PositiveIntegerField(verbose_name='맑음', default=1)
    foggy = models.PositiveIntegerField(verbose_name='안개', default=1)
    rainy = models.PositiveIntegerField(verbose_name='비', default=1)
    cloudy = models.PositiveIntegerField(verbose_name='흐림', default=1)
    snowy = models.PositiveIntegerField(verbose_name='눈', default=1)

    def __str__(self):
        return self.name_music

    # TODO MP3 앨범이미지 저장하기
    # def get_mp3(self, current):
    #     for path, dirs, files in os.walk(current):
    #         if files:
    #             for f in files:
    #                 name = os.path.splitext(f)


# 사용자의 위치를 받아와 날씨정보 1시간마다 DB에 업데이트
class Weather(models.Model):
    latitude = models.FloatField(verbose_name='위도')
    longitude = models.FloatField(verbose_name='경도')
    location = models.CharField(max_length=100)
    time_saved = models.DateTimeField(auto_now_add=True)
    cur_weather = models.CharField(max_length=100)

    # TODO main페이지 url-get요청일 경우 view에서 처리하는 것으로.
    def get_location_info(self):
        """
        구글 역지오코딩을 사용해 위도/경도 정보를 사용자 위치정보를 리턴하고
        해당 인스턴스에 정보 저장
        :param lat: 위도(horizontal location) 정보
        :param long: 경도(vertical location) 정보
        :return: 사용자 위치정보
        """
        lat = self.latitude
        long = self.longitude
        google_api_key = config.settings.GOOGLE_API_KEY
        url = 'https://maps.googleapis.com/maps/api/geocode/json' \
              '?latlng={lat},{long}' \
              '&key={key}' \
              '&language=ko' \
              '&result_type={result_type}'.format(lat=lat,
                                                  long=long,
                                                  key=google_api_key,
                                                  result_type="sublocality"
                                                  )
        addr = requests.get(url).json()['results'][1]['address_components'][2]['long_name']
        self.location = addr
        return addr

    # TODO 날씨 정보 라이브러리 사용하지 않고 불러와 저장하기
    # def get_weather_info(self):
    #     """
    #     날씨 정보 API를 통해 위도/경도 정보로 해당 지역의 날씨정보를 리턴하고
    #     해당 인스턴스에 정보 저장
    #     :param lat: 위도(horizontal location) 정보
    #     :param long: 경도(vertical location) 정보
    #     :return: 사용자 위치의 날씨 정보
    #     """
    #     lat = self.latitude
    #     long = self.longitude
    #     key = config.settings.DARKSKY_API_KEY
    #     fio = ForecastIO.ForecastIO(key,
    #                                 latitude=lat,
    #                                 longitude=long
    #                                 )
    #     current = FIOCurrently.FIOCurrently(fio)
    #     import time
    #     # TODO 요청을 보낸 시간만 추출하여 1시간이 지났으면 날씨정보 업데이트
    #     cur_hour = time.gmtime(current.time).tm_hour
    #     if abs(cur_hour - self.time_saved.hour) > 1:
    #         self.get_weather_info()
    #     cur_icon = current.icon
    #     self.weather = cur_icon
    #     self.weather.save()
    #     return cur_icon


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
