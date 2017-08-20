# from forecastiopy import *

from random import randint

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
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
    lyrics = models.TextField(
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
        "rain": "rainy",
        "snow": "snowy",
        "wind": "sunny",
        "sleet": "foggy",
        "fog": "foggy",
        "partly-cloudy-day": "cloudy",
        "partly-cloudy-night": "cloudy",
        "cloudy": "cloudy",

    }

    # a = [37.497799, 127.027482] # test 좌표
    def _get_location_info(self, latitude, longitude):
        url = "https://maps.googleapis.com/maps/api/geocode/json" \
              "?latlng={LATITUDE},{LONGITUDE}" \
              "&key={SECRET_KEY}" \
              "&language=ko".format(LATITUDE=latitude,
                                    LONGITUDE=longitude,
                                    SECRET_KEY=settings.GOOGLE_API_KEY, )

        # TODO 날씨 구단위로
        data = requests.get(url).json()
        try:
            addr = data["results"]
            if len(addr) > 6:
                location = addr[5]["formatted_address"]
            else:
                location = addr[0]["formatted_address"]
        except Exception as e:
            location = "Fantasy"
        return location

    def _get_weather_info(self, latitude, longitude):
        url = "https://api.darksky.net/forecast/" \
              "{SECRET_KEY}/" \
              "{LATITUDE},{LONGITUDE}".format(SECRET_KEY=settings.DARKSKY_API_KEY,
                                              LATITUDE=latitude,
                                              LONGITUDE=longitude, )
        data = requests.get(url=url).json()
        current_weather = self.weather_dict[data["currently"]["icon"]]
        temperature = round((data["currently"]["temperature"] - 32) / 1.8, 2)
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
        return weather


class MusicManager(models.Manager):
    def get_weather_musics(self, weather):
        """
            1시간에 한번씩 작동하도록?
            weather로 들어온 날씨의 상위곡 12개 출력
        :param weather: 출력할 날씨
        :return: 날씨 상위곡 12개
        """
        return self.order_by("-" + weather)[:12]

    def create_dummy(self, song_name):
        # for Test
        a = []
        while sum(a) == 0:
            a = [randint(0, 10) for x in range(5)]
        self.create(
            img_music="a",
            source_music="aa",
            name_music=song_name,
            name_artist="yh",
            sunny=a[0],
            foggy=a[1],
            rainy=a[2],
            cloudy=a[3],
            snowy=a[4],

        )


# 전체 음악파일/정보 모델
class Music(models.Model):
    # TODO artist || nameMusic으로 index생성 고려

    objects = MusicManager()
    img_music = models.CharField(
        max_length=256,
        null=False,
        blank=False,
    )
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
    lyrics = models.TextField(
        blank=True,
        default="가사정보가 없습니다.",
    )

    sunny = models.PositiveIntegerField(
        editable=True,
        verbose_name='맑음', default=0)
    foggy = models.PositiveIntegerField(
        editable=True,
        verbose_name='안개', default=0)
    rainy = models.PositiveIntegerField(
        editable=True,
        verbose_name='비', default=0)
    cloudy = models.PositiveIntegerField(
        editable=True,
        verbose_name='흐림', default=0)
    snowy = models.PositiveIntegerField(
        editable=True,
        verbose_name='눈', default=0)

    def add_weather(self, weather):
        if weather == "sunny":
            self.sunny += 1
        elif weather == "foggy":
            self.foggy += 1
        elif weather == "rainy":
            self.rainy += 1
        elif weather == "cloudy":
            self.cloudy += 1
        elif weather == "snowy":
            self.snowy += 1
        else:
            print("Wrong weather")
        self.save()

    def __str__(self):
        return self.name_music

    def weather_counts(self):
        return "sunny={sunny} foggy={foggy} rainy={rainy} cloudy={cloudy} snowy={snowy}".format(
            sunny=self.sunny,
            foggy=self.foggy,
            rainy=self.rainy,
            cloudy=self.cloudy,
            snowy=self.snowy,
        )


class Weather(models.Model):
    object = WeatherManager()
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


class PlaylistManager(models.Manager):
    def make_playlist_id(self):
        users = User.objects.prefetch_related("playlists").all()
        for user in users:
            # playlists = Playlist.objects.prefetch_related("user").filter(user=user).order_by("pk")
            playlists = user.playlists.all()
            for i, playlist in enumerate(playlists):
                playlist.make_weather()
                playlist.playlist_id = i + 1
                playlist.save()

    def make_playlist_weather(self):
        # list의 날씨만들기
        playlists = Playlist.objects.all()
        for playlist in playlists:
            playlist.make_weather()

    def make_weather_recommand_list(self, **kwargs):
        """
           추천리스트 생성, 1시간 단위
        :return:
        """
        play_lists = self.filter(user_id=1)  # TODO 필터 조건을 좀더 정교하게
        for play_list in play_lists:
            if not len(play_list.playlist_musics.all()):  # 모종의 사건으로 메인리스트 음악 유실시
                musics = Music.objects.all().order_by("-" + play_list.weather)[:20]
                play_list.playlist_musics.all().delete()

                play_list.add_musics(musics=musics)
            if (timezone.now() - play_list.date_added).seconds >= 3600:  # 업데이트된지 시간이 1시간이 지났을시
                musics = Music.objects.all().order_by("-" + play_list.weather)[:20]
                # play_list.playlist_musics.all().delete()
                PlaylistMusics.objects.select_related("name_playlist").filter(
                    name_playlist=play_list).delete()
                play_list.add_musics(musics=musics)
            self.make_playlist_id()

    def create_main_list(self, ):
        """
            최초 메인 추천리스트 생성
        :return: 추천리스트 5개
        """
        admin = User.objects.get(pk=1)  # filter is_superuser true?

        if len(self.filter(user=admin)) > 4:
            return self.all()[:4]

        Playlist.objects.select_related("user").filter(user=admin).delete()

        sunny, _ = self.get_or_create(user=admin, name_playlist="sunny", weather="sunny")
        sunny.make_id()
        foggy, _ = self.get_or_create(user=admin, name_playlist="foggy", weather="foggy")
        foggy.make_id()
        rainy, _ = self.get_or_create(user=admin, name_playlist="rainy", weather="rainy")
        rainy.make_id()
        cloudy, _ = self.get_or_create(user=admin, name_playlist="cloudy", weather="cloudy")
        cloudy.make_id()
        snowy, _ = self.get_or_create(user=admin, name_playlist="snowy", weather="snowy")
        snowy.make_id()
        self.make_weather_recommand_list()
        self.make_playlist_id()

        return sunny, foggy, rainy, cloudy, snowy


# 유저별 플레이리스트 모델
class Playlist(models.Model):
    objects = PlaylistManager()
    user = models.ForeignKey(
        User,
        related_name="playlists",
        on_delete=models.CASCADE
    )
    name_playlist = models.CharField(
        max_length=30,
        default='playlist'
    )
    weather = models.CharField(
        max_length=10,
        default="false",
    )
    playlist_musics = models.ManyToManyField(
        'Music',
        through='PlaylistMusics',
        related_name='playlist_musics',
    )
    playlist_id = models.PositiveSmallIntegerField(
        default=0,
    )
    # main list용
    # 이 시간 마지막이 1시간이 넘으면 add
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "name_playlist")

    def delete_music(self, music_pk):
        # 예외처리
        # --> apiView에서 처리
        music = Music.objects.get(pk=music_pk)
        PlaylistMusics.objects.select_related("music").get(
            name_playlist=self,
            music=music,
        ).delete()

    # TODO 임시방편 manager에 넣는게 좋을듯, filter시 id최대값 +1로 변경
    def make_id(self):
        self.playlist_id = len(Playlist.objects.filter(user=self.user))
        self.save()
        return self.playlist_id

    @property
    def make_list_attribute_weather(self):
        """
            이 list의 대표 날씨를 뽑는다
            우선은 단순히 날씨별 가장 높은 것을 카운트
        :return:
        """

        results = self.playlist_musics.aggregate(
            sunny=Sum("sunny"),
            foggy=Sum("foggy"),
            rainy=Sum("rainy"),
            cloudy=Sum("cloudy"),
            snowy=Sum("snowy"),
        )
        try:
            return max(results, key=lambda i: results[i])
        except Exception as e:
            return "빈 리스트"

    def make_weather(self):
        self.weather = self.make_list_attribute_weather
        pass

    def add_music(self, music):

        # TODO 아마 사용은 주소로 들어올테니 music 객체를 찾도록 추후 수정
        """
        음악을 리스트에 추가하고 weather필드에 날씨 업데이트
        :param music: 리스트에 들어갈 음악
        :return:
        """
        self.playlistmusics_set.create(music=music)
        self.weather = self.make_list_attribute_weather
        music.add_weather(self.weather)
        self.save()
        return self

    def add_musics(self, musics):
        for music in musics:
            self.playlistmusics_set.create(music=music)
        self.weather = self.make_list_attribute_weather
        music.add_weather(self.weather)
        self.save()

        return self

    def __str__(self):
        return '{}의 {}'.format(
            self.user,
            self.name_playlist)  # 유저의 플레이리스트 내 음악 목록 모델


class PlaylistMusics(models.Model):
    name_playlist = models.ForeignKey(
        'Playlist',
        on_delete=models.CASCADE)
    music = models.ForeignKey(
        'Music',
        related_name="musics",
        on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '리스트 {}의 음악 {}'.format(
            self.name_playlist,
            self.music
        )
