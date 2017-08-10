import os

import eyed3
from django.conf import settings

__all__ = (
    "add_mp3_and_album_image_in_database",

)


# TODO 반드시 리팩터링!!!!!!!!
def add_mp3_and_album_image_in_database(current=settings.STATIC_DIR + "/musics"):
    from music.models import Music
    # 음악들이 존재하는 폴더

    addr_music = "https://s3.ap-northeast-2.amazonaws.com/weather-sound-test-s3-bucket/media/musics/"
    addr_img = "https://s3.ap-northeast-2.amazonaws.com/weather-sound-test-s3-bucket/media/musics/images/"
    cur_path = "{}/{}".format(settings.STATIC_DIR, "musics")
    img_address = cur_path + "/images/"

    if not os.path.isdir(img_address):
        os.mkdir(img_address)

    extens = [".mp3", ]  # 음원 파일로 설정할 확장자들
    for path, dirs, files in os.walk(current):
        # (path 경로), (dirs 폴더들), (files dir내 파일들)
        if files:
            for f in files:
                print(11111111111111111, f)
                print()
                print()
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

                        # TODO album name중복 추후 .
                        with open(img_address + "{}.jpg".format(album), "wb") as f:  # 추후 image저장위치 지정 다시
                            f.write(img)

                    source_music = addr_music + "/" + f
                    print(source_music)
                    m = Music.objects.create(
                        # space bar -> "+" 로 변환?
                        source_music=source_music,
                        name_music=audio.tag.title,
                        name_artist=artist,
                        name_album=album,
                        img_music="{}{}".format(addr_img, "{}-{}.jpg".format(artist, album)),
                    )
                    print(m.source_music, "\n ",
                          m.name_music, "\n ",
                          m.name_artist, "\n ",
                          m.name_album, "\n ",
                          m.img_music)
                    print()
