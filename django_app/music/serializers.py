from django.contrib.auth import get_user_model
from rest_framework import serializers

from music.models import Music, Playlist, PlaylistMusics

User = get_user_model()

__all__ = (
    "MusicSerializer",
    "PlaylistSerializer",
    "UserPlaylistSerializer",

)


class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = (
            'id',
            'img_music',
            'name_music',
            'name_artist',
            'source_music',
            "lyrics",
        )


class PlaylistSerializer(serializers.ModelSerializer):
    playlist_musics = MusicSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = (
            "pk",
            "name_playlist",
            "weather",
            "playlist_musics"

        )


class PlaylistMusicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistMusics
        fields = (
            "name_playlist",
            "music",
        )

    pass


class UserPlaylistSerializer(serializers.ModelSerializer):
    playlists = PlaylistSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "nickname",
            "playlists",
            # "playlist_set",

        )

# class PlaylistSerializer(serializers.ModelSerializer):
#     # user = UserPlaylistSerializer()
#
#     class Meta:
#         model = Playlist
#         fields = (
#             "name_playlist",
#             "weather",
#             # "user",
#         )
