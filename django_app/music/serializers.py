from rest_framework import serializers

from music.models import Music


class MusicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Music
        fields = (
            'id',
            'img_music',
            'name_music',
            'name_singer',
            'file_music',
        )
