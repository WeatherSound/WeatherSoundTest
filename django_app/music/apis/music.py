from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
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
    # "UserPlaylistListCreateView",
    "MainPlaylistListView",
    "UserMusiclistRetrieveUpdateDestroy",

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
    """
        Main Recommander List
        list : 5가지의 날씨를 다 보여준다
        post (날씨) : 그 날씨에 맞는 리스트의 곡리스트를 보여준다
    """
    queryset = Playlist.objects.filter(user=1)
    serializer_class = PlaylistSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PlaylistSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        weathers = (
            "sunny",
            "foggy",
            "rainy",
            "cloudy",
            "snowy",
        )
        weather = request.data.get("name", None)

        # TODO 효율을 위해서 그 한 리스트에서 날씨에 맞는 리스트를 뽑도록 할까?
        if weather in weathers:
            Playlist.objects.make_weather_recommand_list()
            try:
                queryset = Playlist.objects.get(
                    user=1,
                    name_playlist=weather,
                )
            except Playlist.DoesNotExist as e:
                Playlist.objects.create_main_list()
            serializer = self.serializer_class(queryset)
            content = {
                "detail": "Main list {}.".format(weather),
                "listInfo": serializer.data,
            }
            return Response(content, status.HTTP_202_ACCEPTED)
        content = {
            "detail": "Wrong Weather.",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST)


class UserMusiclistRetrieveUpdateDestroy(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPlaylistSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ObjectIsRequestUser,
    )

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs["pk"])
        except User.DoesNotExist as e:
            context = {
                "detail": "user does not exists",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        serializer_class = UserPlaylistSerializer
        serializer = serializer_class(user)
        context = {
            "User": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)

    # TODO 리스트 내에 음악 중복처리
    def put(self, request, *args, **kwargs):  # make peronal list
        try:
            user = User.objects.get(pk=kwargs["pk"])
            music_pk = request.data.get("music_added", None)
        except User.DoesNotExist as e:
            context = {
                "detail": "User does not exist",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        serializer_class = UserPlaylistSerializer
        pl_name = request.data.get('name_playlist', None)
        if not pl_name:
            context = {
                "detail": "Enter Playlist"
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        pl, pl_created = Playlist.objects.get_or_create(user=user, name_playlist=pl_name)
        if music_pk:
            try:
                music = Music.objects.get(pk=music_pk)
            except Music.DoesNotExist as e:
                content = {
                    "detail": "Wrong Music",
                }
                return Response(content, status=status.HTTP_404_NOT_FOUND)
            else:
                pl.add_music(music=music)
                pl.make_id()
        serializer = serializer_class(user)
        context = {
            "detail": "Created",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)


# 개인 플레이리스트 디테일
class UserPlayListMusicsRetrieveDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = PlaylistSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = (
        permissions.IsAuthenticated,
        # ObjectIsRequestUser,
    )

    def get(self, request, *args, **kwargs):
        try:
            playlist = kwargs["playlist_pk"]
            user = self.queryset.get(pk=kwargs["pk"])
            queryset = Playlist.objects.get(user=user, playlist_id=playlist)
        except User.DoesNotExist as e:
            context = {
                "detail": "User does not exists",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except Playlist.DoesNotExist as e:
            context = {
                "detail": "Playlist Does not Exists"
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        # serializer_class = PlaylistSerializer
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        music_deleted = request.data.get("music_deleted", None)
        if music_deleted:
            try:
                pk = kwargs["pk"]
                playlist_pk = kwargs["playlist_pk"]
                playlist = Playlist.objects.get(
                    user_id=pk,
                    playlist_id=playlist_pk,
                )
                music = playlist.playlist_musics.get(pk=music_deleted)
            except Playlist.DoesNotExist as e:
                context = {
                    "detail": "Playlist does not exsits",
                }
                return Response(context, status=status.HTTP_404_NOT_FOUND)
            except Music.DoesNotExist as e:
                context = {
                    "detail": "Music does not exsists",
                }
                return Response(context, status=status.HTTP_404_NOT_FOUND)
            music.delete()
            # TODO 빈 리스트면 삭제
            # Playlist.objects.make_playlist_id()
            user = self.queryset.get(pk=kwargs["pk"])
            queryset = Playlist.objects.get(user=user, playlist_id=playlist.playlist_id)
            context = {
                "detail": "삭제 성공",
                "playlist": self.serializer_class(queryset).data,
            }
            return Response(context, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        try:
            playlist = kwargs["playlist_pk"]
            user = self.queryset.get(pk=kwargs["pk"])
            queryset = Playlist.objects.get(user=user, playlist_id=playlist)
        except User.DoesNotExist as e:
            context = {
                "detail": "User does not exists",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except Playlist.DoesNotExist as e:
            context = {
                "detail": "Playlist Does not Exists"
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        queryset.delete()
        # TODO 고치기
        Playlist.objects.make_playlist_id()
        context = {
            "detail": "리스트가 삭제되었습니다."
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)


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
        # class UserPlaylistListCreateView(APIView):
        #     def get(self, request, *args, **kwargs):
        #         # TODO 유저별로 판단 가능하게!
        #         users = User.objects.all()
        #         serializer = UserPlaylistSerializer(users, many=True)
        #         return Response(serializer.data)
        #
        #     def post(self, request, *args, **kwargs):
        #         pass

        # class PlaylistMusicsListCreateView(APIView):
        #     def get(self, request, *args, **kwargs):
        #         plm = PlaylistMusics.objects.all()
        #         serializer = PlaylistMusicsSerializer(plm, many=True)
        #         return Response(serializer.data)
        #
        #     pass
