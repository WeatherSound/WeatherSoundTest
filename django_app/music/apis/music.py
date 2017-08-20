from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Music, Playlist, PlaylistMusics, Weather
from music.permissions import IsOwnerOrReadOnly
from music.serializers import MusicSerializer, PlaylistSerializer, UserPlaylistSerializer, MainPlaylistSerializer
from permissions import ObjectIsRequestUser

__all__ = (
    'MusicListCreateView',
    'MusicListView',
    "PlaylistListCreateView",
    "MainPlaylistListView",
    "UserMusiclistRetrieveUpdateDestroy",

)

User = get_user_model()


class MusicListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        musics = Music.objects.all()
        serializer = MusicSerializer(musics, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        pass


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
    queryset = Playlist.objects.prefetch_related("playlist_musics").filter(user=1)
    serializer_class = MainPlaylistSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MainPlaylistSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # 없을시, 숫자가 아닐시
        latitude = request.data.get("latitude", None)
        longitude = request.data.get("longitude", None)
        number = request.data.get("number", None)
        if latitude and longitude:
            try:
                weather = Weather.object.create_or_update_weather(latitude, longitude)
                Playlist.objects.make_weather_recommand_list()
                queryset = self.queryset.get(name_playlist=weather.current_weather)
            except Playlist.DoesNotExist as e:
                Playlist.objects.create_main_list()
            else:
                serializer = self.serializer_class(queryset)
                content = {
                    "context": "Main list {}.".format(weather.current_weather),
                    "address": weather.location,
                    "weather": weather.current_weather,
                    "temperature": weather.temperature,
                    "listInfo": serializer.data,
                }
                return Response(content, status.HTTP_202_ACCEPTED)
        content = {
            "detail": "Enter correct Latitude and Longitude",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST)

        # def post(self, request, *args, **kwargs):
        #     weathers = (
        #         "sunny",
        #         "foggy",
        #         "rainy",
        #         "cloudy",
        #         "snowy",
        #     )
        #     weather = request.data.get("weathers", None)
        #
        #     if weather in weathers:
        #         Playlist.objects.make_weather_recommand_list()
        #         try:
        #             queryset = self.queryset.get(name_playlist=weather)
        #         except Playlist.DoesNotExist as e:
        #             Playlist.objects.create_main_list()
        #         serializer = self.serializer_class(queryset)
        #         content = {
        #             "detail": "Main list {}.".format(weather),
        #             "listInfo": serializer.data,
        #         }
        #         return Response(content, status.HTTP_202_ACCEPTED)
        #     content = {
        #         "detail": "Wrong Weather.",
        #         "description": "sunny, foggy, rainy, cloudy, snowy",
        #     }
        #     return Response(content, status.HTTP_400_BAD_REQUEST)


# User의 모든 playlists
class UserMusiclistRetrieveUpdateDestroy(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPlaylistSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ObjectIsRequestUser,
    )

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_queryset().get(pk=kwargs["pk"])
        except User.DoesNotExist as e:
            context = {
                "detail": "user does not exists",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user)
        context = {
            "User": serializer.data,
        }
        return Response(context, status=status.HTTP_200_OK)

    # TODO 리스트 내에 음악 중복처리
    # 플레이리스트 리스트 + 리스트에 음악 추가
    def put(self, request, *args, **kwargs):  # make peronal list
        # Playlist Name이 존재하면
        pl_name = request.data.get('name_playlist', None)
        if not pl_name:
            context = {
                "detail": "Enter Playlist"
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        try:
            user = self.get_queryset().get(pk=kwargs["pk"])
            music_pk = request.data.get("music", None)
        except User.DoesNotExist as e:
            context = {
                "detail": "User does not exist",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        pl, pl_created = Playlist.objects.get_or_create(user=user, name_playlist=pl_name)
        Playlist.objects.make_playlist_id()
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

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(user)
        context = {
            "detail": "Created",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)


# 개인 플레이리스트 디테일
class UserPlayListMusicsRetrieveDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.prefetch_related("playlists").all()
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
            # queryset = Playlist.objects.get(user=user, playlist_id=playlist)
            queryset = Playlist.objects.select_related("user").get(
                user=user,
                playlist_id=playlist,
            )
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

        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    # Playlist 음악 삭제
    def put(self, request, *args, **kwargs):
        music_deleted = request.data.get("music", None)
        if music_deleted:
            try:
                pk = kwargs["pk"]
                playlist_pk = kwargs["playlist_pk"]
                playlist = Playlist.objects.prefetch_related("user").get(
                    user_id=pk, playlist_id=playlist_pk)
                music = playlist.playlist_musics.filter(pk=music_deleted)
                # playlist.playlist_musics.filter(id=music[0].id).delete()
                PlaylistMusics.objects.filter(
                    name_playlist__playlist_id=playlist_pk,
                    music=music,
                ).delete()

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
            except Exception as e:
                context = {
                    "detail": "Enter Integer",
                }
                return Response(context, status=status.HTTP_406_NOT_ACCEPTABLE)
            user = self.queryset.get(pk=kwargs["pk"])
            queryset = Playlist.objects.prefetch_related("user").get(
                user=user, playlist_id=playlist.playlist_id)
            context = {
                "detail": "삭제 성공",
                "playlist": self.serializer_class(queryset).data,
            }
            # TODO 삭제시에도 리스트 날씨 갱신
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
