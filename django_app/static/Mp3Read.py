import hashlib
import os
from random import randint

import eyed3
from django.conf import settings

from music.models import Music


# TODO 반드시 리팩터링!!!!!!!!



def add_mp3_and_album_image_in_database():
    """
        고의적으로 static폴더 안에만 있는 파일들만 작동하도록 하였다
        static/musics 의 안에 있는 모든 음악 파일들의 이름을
            sha256으로 암호화 + 앨범이미지(가수명 + 앨범명)으로 암호화
    :return: None
    """
    # 음악들이 존재하는 폴더
    static_dir = settings.STATIC_DIR
    cur_path = os.path.join(static_dir, "musics")
    img_address = os.path.join(cur_path, "images")
    # addr_music = "https://s3.ap-northeast-2.amazonaws.com/weather-sound-test-s3-bucket/static/musics/"
    addr_music = "https://s3.{s3_region}.amazonaws.com/{s3_bucket_name}/{static}/{musics}".format(
        s3_region=settings.AWS_S3_REGION_NAME,
        s3_bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
        static="static",
        musics="musics",
    )
    addr_img = os.path.join(addr_music, "images")

    if not os.path.isdir(img_address):
        # musics/images 폴더 생성
        os.mkdir(img_address)

    extens = [".mp3", ]  # 음원 파일로 설정할 확장자들
    for path, dirs, files in os.walk(cur_path):
        # (path 경로), (dirs 폴더들), (files dir내 파일들)
        if files:
            for f in files:
                name = os.path.splitext(f)  # 파일명, 확장자로 나눈다

                if name[1] in extens:  # 확장자가 extens에 존재하면
                    # audio = eyed3.load(os.path.join(cur_path, f))
                    audio = eyed3.load(os.path.join(path, f))  # 지금 폴더의 음악
                    hashed_name = "{name}{name_extention}".format(  # 파일명 암호화
                        name=hashlib.sha256(name[0].encode("utf-8")).hexdigest(),
                        name_extention=name[1],
                    )
                    if audio.tag.album is None:  # 음악 tag에 album정보가 없으면
                        album = "nonamed"  # 임의로 nonamed -> 상용화하는 파일이라면 무조건 있어야한다
                    else:
                        album = audio.tag.album
                        artist = audio.tag.artist

                    if not os.path.isfile(artist + "-" + album + ".jpg"):  # image파일은 "음악가-앨범이름"으로 구성
                        img = audio.tag.images[0].image_data  # 앨범에 여러 사진을 넣을수도 있기에 첫 사진을 기준
                        img_name = hashlib.sha256(
                            "/{}-{}".format(artist, album).encode("utf-8")).hexdigest()  # img_name

                        with open(img_address + "/{}.jpg".format(img_name), "wb") as ff:  # 추후 image저장위치 지정 다시
                            ff.write(img)

                    m = Music.objects.create(
                        source_music="{}/{}".format(addr_music, hashed_name),
                        name_music=audio.tag.title,
                        name_artist=artist,
                        name_album=album,
                        img_music="{}/{}.jpg".format(addr_img, img_name),
                        time_music=audio.info.time_secs,

                        # TODO 더미용 날씨 데이터
                        sunny=randint(0, 1),
                        foggy=randint(0, 1),
                        rainy=randint(0, 1),
                        cloudy=randint(0, 1),
                        snowy=randint(0, 1),

                    )
                    print(11111111, path)
                    os.rename(path + "/" + f, path + "/" + hashed_name)
                    print(m.source_music, " ",
                          m.name_music, " ",
                          m.name_artist, " ",
                          m.name_album, " ",
                          m.img_music)
                    print("hey")
