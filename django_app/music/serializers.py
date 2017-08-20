from django.contrib.auth import get_user_model
from rest_framework import serializers

from music.models import Music, Playlist

User = get_user_model()

__all__ = (
    "MainPlaylistSerializer",
    "MusicSerializer",
    "PlaylistSerializer",
    "UserPlaylistSerializer",
    "RetrieveUpdateDestroyAPIView",

)


# Music
class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = (
            'pk',
            'img_music',
            'name_music',
            'name_artist',
            'source_music',
            "time_music",
            "lyrics",
        )


class MainPlaylistSerializer(serializers.ModelSerializer):
    playlist_musics = MusicSerializer(many=True, read_only=True)
    # weathers = serializers.CharField(
    #     help_text="sunny, foggy, rainy, cloudy, snowy",
    #     label="weather",
    #     max_length=10,
    #     allow_blank=True,
    #     write_only=True,
    # )
    latitude = serializers.CharField(
        help_text="Latitute",
        label="Latitute",
        max_length=10,
        allow_blank=True,
        write_only=True,

    )
    longitude = serializers.CharField(
        help_text="Longitude",
        label="Longitude",
        max_length=10,
        allow_blank=True,
        write_only=True,
    )

    # number = serializers.CharField(
    #     help_text="Number of Musics",
    #     label="Number",
    #     max_length=2,
    #     allow_blank=True,
    #     write_only=True,
    # )

    class Meta:
        model = Playlist
        fields = (
            "pk",
            "name_playlist",
            "weather",
            "playlist_id",
            "playlist_musics",
            # "weathers",
            "latitude",
            "longitude",
            # "number",
        )

        read_only_fields = (
            "name_playlist",
            "playlist_id",
            "weather",
        )


# musics < Playlist
class PlaylistSerializer(serializers.ModelSerializer):
    playlist_musics = MusicSerializer(many=True, read_only=True)
    music = serializers.CharField(
        label="music deleted",
        max_length=10,
        allow_blank=True,
        write_only=True,
    )

    class Meta:
        model = Playlist
        fields = (
            "pk",
            "name_playlist",
            "weather",
            "playlist_id",
            "playlist_musics",
            "music",
        )

        read_only_fields = (
            "name_playlist",
            "playlist_id",
            "weather",
        )


# musics < playlists < User
class UserPlaylistSerializer(serializers.ModelSerializer):
    playlists = PlaylistSerializer(
        many=True,
        read_only=True,
    )
    name_playlist = serializers.CharField(
        label='PlayList Name',
        max_length=30,
        allow_blank=True,
        write_only=True,  # 주의
    )
    music = serializers.CharField(
        label="Music added",
        max_length=4,
        allow_blank=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "pk",
            "username",  # email
            "nickname",  # nickname
            "playlists",
            "name_playlist",
            "music",
        )
        read_only_fields = (
            "username",
            "nickname",
            "playlists",
        )
        extra_kwargs = {
            'name_playlist': {'write_only': True},
        }
