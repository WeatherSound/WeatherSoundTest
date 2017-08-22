from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Music, Playlist, Weather
from music.permissions import IsOwnerOrReadOnly
from music.serializers import MusicSerializer, PlaylistSerializer, UserPlaylistSerializer, MainPlaylistSerializer, \
    UserSharedPlaylistSerializer
from permissions import ObjectHasPermission, ObjectIsRequestUser

__all__ = (
    'MusicListCreateView',
    'MusicListView',
    "PlaylistListCreateView",
    "MainPlaylistListView",
    "UserMusiclistRetrieveUpdateDestroy",
    "UserSharedListUpdate",

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
    queryset = Playlist.objects.select_related("user").prefetch_related(
        "playlist_musics").filter(user=User.objects.filter(is_superuser=True).first())  # 첫번째 유저가 admin이라는 전제하에
    serializer_class = MainPlaylistSerializer

    def get(self, request, *args, **kwargs):  # 5가지 날씨의 추천리스트를 보여준다
        Playlist.objects.create_main_list()
        queryset = self.get_queryset()
        serializer = MainPlaylistSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
            위도와 경도를 입력받아 해당 지역에 맞는 추천리스트를 토한다
        :return: 5가지 추천리스트 중 1개
        """
        latitude = request.data.get("latitude", None)
        longitude = request.data.get("longitude", None)
        try:
            float(latitude), float(longitude)  # 입력 string이 float형이 아니면 예외처리
            weather = Weather.object.create_or_update_weather(latitude, longitude)
            Playlist.objects.create_main_list()  # main list check목적
            queryset = self.queryset.get(name_playlist=weather.current_weather)
        except Exception as e:
            content = {
                "detail": "Enter correct Latitude and Longitude",
            }
            return Response(content, status.HTTP_400_BAD_REQUEST)
        else:
            # 예외 처리가 일어나지 않으면 정상 작동처리
            serializer = self.serializer_class(queryset)
            content = {
                "context": "Main list {}.".format(weather.current_weather),
                "address": weather.location,
                "weather": weather.current_weather,
                "temperature": weather.temperature,
                "listInfo": serializer.data,
            }
            return Response(content, status.HTTP_202_ACCEPTED)


# User의 모든 playlists
class UserMusiclistRetrieveUpdateDestroy(generics.RetrieveUpdateAPIView):
    queryset = User.objects.prefetch_related("playlists").all()
    serializer_class = UserPlaylistSerializer
    permission_classes = (  # TODO 퍼미션 체크 확실히
        permissions.IsAuthenticated,
        # ObjectHasPermission,
        ObjectIsRequestUser,
    )

    # 개인이 가진 모든 플레이 리스트
    def get(self, request, *args, **kwargs):
        try:
            user = self.get_queryset().get(pk=kwargs["pk"])
        except User.DoesNotExist as e:
            context = {
                "detail": "user does not exists",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.get_serializer(user)
            context = {
                "User": serializer.data,
            }
            return Response(context, status=status.HTTP_200_OK)

    # TODO 리스트 내에 음악 중복처리
    # Playlist 추가 + 음악추가
    def post(self, request, *args, **kwargs):
        try:
            pl_name = request.data.get('create_playlist', None)
            user = self.get_queryset().get(pk=kwargs["pk"])  # user find
            pl, pl_created = Playlist.objects.get_or_create(user=user, name_playlist=pl_name)  # pl create or find
            music_pks = request.data.get("music", None)  # get music  pk
            music_pks = [pk.strip() for pk in music_pks.split(",") if pk]
            pl.add_musics_string(music_pks)
        except User.DoesNotExist as e:
            context = {
                "detail": "User Does not exist",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except Music.DoesNotExist as e:
            context = {
                "detail": "Music Does not exist",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except TypeError or Playlist.DoesNotExist as e:
            context = {
                "detail": "Enter Playlist Name",
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        # user = User.objects.get(pk=user)
        # serializer_class = self.get_serializer_class()
        serializer = PlaylistSerializer(pl)
        context = {
            "detail": "Created",
            "lists": serializer.data,
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)

    # Playlist 삭제
    def put(self, request, *args, **kwargs):
        try:
            delete_playlists = request.data.get("delete_playlist", None)
            delete_playlists = [playlist.strip() for playlist in delete_playlists.split(",") if playlist]
            Playlist.objects.delete_playlists(delete_playlists)
        except User.DoesNotExist as e:
            context = {
                "detail": "User does not exist",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            context = {
                "detail": "Enter Playlist PKs",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except Playlist.DoesNotExist as e:
            context = {
                "detail": "Enter Right Playlist PKs",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            context = {
                "detail": e,
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        else:
            context = {
                "detail": "List Delete Success",
                "list deleted": delete_playlists,
            }
            return Response(context, status=status.HTTP_202_ACCEPTED)


# 개인 플레이리스트 디테일
class UserPlayListMusicsRetrieveDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.prefetch_related("playlists").all()
    serializer_class = PlaylistSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = (
        permissions.IsAuthenticated,
        ObjectHasPermission,  # 내꺼
    )

    def get(self, request, *args, **kwargs):
        try:
            playlist = kwargs["playlist_pk"]
            queryset = Playlist.objects.select_related("user").get(
                pk=playlist,
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
        else:
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)

    # Playlist 음악 삭제
    def put(self, request, *args, **kwargs):
        deleted_musics = request.data.get("music", None)
        try:
            deleted_musics = [musics.strip() for musics in deleted_musics.split(",") if musics]
            playlist_pk = kwargs["playlist_pk"]
            playlist = Playlist.objects.get(pk=playlist_pk)
            playlist.delete_musics_string(deleted_musics)
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
        queryset = Playlist.objects.get(pk=playlist.pk)
        context = {
            "detail": "삭제 성공",
            "playlist": self.serializer_class(queryset).data,
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        try:
            playlist = kwargs["playlist_pk"]
            user = self.queryset.get(pk=kwargs["pk"])
            queryset = Playlist.objects.get(user=user, pk=playlist.pk)
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
        context = {
            "detail": "리스트가 삭제되었습니다."
        }

        return Response(context, status=status.HTTP_202_ACCEPTED)  # 전체 playlist


class PlaylistListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        playlists = Playlist.objects.all()
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)


class UserSharedListUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Playlist.objects.select_related("user").all()
    serializer_class = UserSharedPlaylistSerializer

    def get(self, request, *args, **kwargs):
        shared_list = self.get_queryset().filter(
            is_shared_list=True,
            user__pk=kwargs["pk"],
        )
        context = {
            # "Shared List": self.serializer_class(shared_list).data,
        }
        return Response(context, status=status.HTTP_200_OK)

    pass
