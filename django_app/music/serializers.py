from django.contrib.auth import get_user_model
from rest_framework import serializers

from music.models import Music, Playlist

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
    class Meta:
        model = Playlist
        fields = (
            "name_playlist",
            "weather",
        )


class UserPlaylistSerializer(serializers.ModelSerializer):
    playlist = PlaylistSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "nickname",
            "playlist",
        )
