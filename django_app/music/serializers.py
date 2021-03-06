from django.contrib.auth import get_user_model
from rest_framework import serializers

from music.models import Music, Playlist

User = get_user_model()

__all__ = (
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
            "lyrics",
        )


# Playlist
# playlst/
class PlaylistSerializer(serializers.ModelSerializer):
    playlist_musics = MusicSerializer(many=True, read_only=True)
    name = serializers.CharField(
        max_length=5,
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
            "name",
        )

        read_only_fields = (
            "name_playlist",
            "playlist_id",
            "weather",
        )


# userplaylist/
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
    music_added = serializers.CharField(
        label="Music",
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
            "music_added",
        )
        read_only_fields = (
            "username",
            "nickname",
            "playlists",
        )
        extra_kwargs = {
            'name_playlist': {'write_only': True},
        }

# class PersonalListAddMusic(serializers.ModelSerializer):
#     class Meta:
#         model = Playlist
#         fields = (
#
#         )
#     pass
