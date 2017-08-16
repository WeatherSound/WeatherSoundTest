from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Music, Playlist
from music.permissions import IsOwnerOrReadOnly
from music.serializers import MusicSerializer, PlaylistSerializer, UserPlaylistSerializer
from permissions import ObjectIsRequestUser

__all__ = (
    'MusicListCreateView',
    'MusicListView',
    "PlaylistListCreateView",
    "UserPlaylistListCreateView",
    "MainPlaylistListView",
    "PersonalMusiclistRetrieveUpdateDestroy",
    # "PlaylistMusicsListCreateView",

)

User = get_user_model()


# APIView 사용
# url 형식 :
# {
#   "id": 1,
#   "img_music": "/media/img_music/logo_icecream.jpg",
#   "name_music": "응프리스타일",
#   "name_singer": "sik-k, punchnello, flowsik",
#   "file_music": "/media/music/EUNG_FREESTYLE_%E1%84%8B%E1%85%B3%E1%86%BC%E1%84%91%E1%85%B3%E1%84%85%E1%85%B5%E1%84%89%E1%85%B3%E1%84%90%E1%85%A1%E1%84%8B%E1%85%B5%E1%86%AF_-_LIVE_SIK-K_PUNCHNELLO_OWEN_OVADOZ_FLOWSIK.mp3"
# },
class MusicListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        musics = Music.objects.all()
        serializer = MusicSerializer(musics, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        pass


# GenericView 사용
# url 형식 :
# {
#   "id": 1,
#   "img_music": "http://localhost:8000/media/img_music/logo_icecream.jpg",
#   "name_music": "응프리스타일",
#   "name_singer": "sik-k, punchnello, flowsik",
#   "file_music": "http://localhost:8000/media/music/EUNG_FREESTYLE_%E1%84%8B%E1%85%B3%E1%86%BC%E1%84%91%E1%85%B3%E1%84%85%E1%85%B5%E1%84%89%E1%85%B3%E1%84%90%E1%85%A1%E1%84%8B%E1%85%B5%E1%86%AF_-_LIVE_SIK-K_PUNCHNELLO_OWEN_OVADOZ_FLOWSIK.mp3"
# },
class MusicListView(generics.ListCreateAPIView):
    queryset = Music.objects.all().order_by('name_album')
    serializer_class = MusicSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        if self.request.user.is_admin:
            serializer.save(owner=self.request.user)


# main list
class MainPlaylistListView(generics.ListAPIView):
    queryset = Playlist.objects.filter(user=1)
    serializer_class = PlaylistSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PlaylistSerializer(queryset, many=True)
        return Response(serializer.data)


class PersonalMusiclistRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserPlaylistSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ObjectIsRequestUser,
    )

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(pk=kwargs["pk"])
        serializer_class = UserPlaylistSerializer
        serializer = serializer_class(user, many=True)
        return Response(serializer.data)

    # TODO 리스트 내에 음악 중복처리
    def put(self, request, *args, **kwargs):  # make peronal list
        user = User.objects.filter(pk=kwargs["pk"])
        music_pk = request.data.get("music_added", None)
        serializer_class = UserPlaylistSerializer
        serializer = serializer_class(user, many=True)
        pl_name = request.data.get('name_playlist')
        if pl_name:
            pl, pl_created = Playlist.objects.get_or_create(user=user[0],
                                                            name_playlist=pl_name)
            if music_pk:
                music = Music.objects.get(pk=music_pk)
                pl.playlistmusics_set.create(music=music)

        serializer = serializer_class(user, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


# 전체 playlist
class PlaylistListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        playlists = Playlist.objects.all()
        # user = User.objects.all()
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)

        # def post(self, request, *args, **kwargs):
        #     pass


# 개인이 소유한 플레이 리스트
class UserPlaylistListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        # TODO 유저별로 판단 가능하게!
        users = User.objects.all()
        serializer = UserPlaylistSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        pass

# class PlaylistMusicsListCreateView(APIView):
#     def get(self, request, *args, **kwargs):
#         plm = PlaylistMusics.objects.all()
#         serializer = PlaylistMusicsSerializer(plm, many=True)
#         return Response(serializer.data)
#
#     pass
