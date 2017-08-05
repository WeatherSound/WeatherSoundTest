import os

import eyed3
# TODO 반드시 리팩터링!!!!!!!!
from django.conf import settings

# from music.models import Music
from music.models import Music


def add_mp3_and_album_image_in_database():
    # 음악들이 존재하는 폴더
    static_dir = settings.STATIC_DIR
    # static_dir = "/Users/HY/projects/TeamProject/WeatherSoundTest/django_app/static/"
    addr_music = "https://s3.ap-northeast-2.amazonaws.com/weather-sound-test-s3-bucket/static/musics/"
    addr_img = os.path.join(addr_music, "images")
    # addr_img = "https://s3.ap-northeast-2.amazonaws.com/weather-sound-test-s3-bucket/static/musics/images/"
    # cur_path = "{}/{}".format(settings.STATIC_DIR, "musics")
    cur_path = os.path.join(static_dir, "musics")
    # cur_path = "{}/{}".format(static_dir, "musics")
    img_address = os.path.join(cur_path, "images")
    # img_address = cur_path + "/images/"

    if not os.path.isdir(img_address):
        os.mkdir(img_address)

    extens = [".mp3", ]  # 음원 파일로 설정할 확장자들
    for path, dirs, files in os.walk(cur_path):
        # (path 경로), (dirs 폴더들), (files dir내 파일들)
        if files:
            for f in files:
                name = os.path.splitext(f)  # 파일명, 확장자로 나눈다
                if name[1] in extens:  # 확장자가 extens에 존재하면
                    audio = eyed3.load(os.path.join(cur_path, f))

                    if audio.tag.album is None:  # 음악 tag에 album정보가 없으면
                        album = "nonamed"  # 임의로 nonamed -> 상용화하는 파일이라면 무조건 있어야한다
                    else:
                        album = audio.tag.album
                        artist = audio.tag.artist

                    if not os.path.isfile(artist + "-" + album + ".jpg"):  # image파일은 "음악가-앨범이름"으로 구성
                        img = audio.tag.images[0].image_data  # 앨범에 여러 사진을 넣을수도 있기에 첫 사진을 기준

                        with open(img_address + "{}-{}.jpg".format(artist, album), "wb") as ff:  # 추후 image저장위치 지정 다시
                            ff.write(img)

                    m = Music.objects.create(
                        # space bar -> "+" 로 변환?
                        source_music="{}{}".format(addr_music, f),
                        name_music=audio.tag.title,
                        name_artist=artist,
                        name_album=album,
                        img_music="{}{}".format(addr_img, "{}-{}.jpg".format(artist, album)),
                    )
                    print(m.source_music, " ",
                          m.name_music, " ",
                          m.name_artist, " ",
                          m.name_album, " ",
                          m.img_music)
                    print("hey")
