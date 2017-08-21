from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Music, Playlist, PlaylistMusics, Weather
from music.permissions import IsOwnerOrReadOnly
from music.serializers import MusicSerializer, PlaylistSerializer, UserPlaylistSerializer, MainPlaylistSerializer
from permissions import ObjectHasPermission

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
    queryset = Playlist.objects.select_related("user").prefetch_related(
        "playlist_musics").filter(user=User.objects.first())  # 첫번째 유저가 admin이라는 전제하에
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
        if latitude and longitude:  # 위도 경도 다 입력되었으면
            try:
                float(latitude), float(longitude)  # 입력 string이 float형이 아니면 예외처리
                weather = Weather.object.create_or_update_weather(latitude, longitude)
                Playlist.objects.create_main_list()
                # Playlist.objects.make_weather_recommand_list()
                queryset = self.queryset.get(name_playlist=weather.current_weather)
            except  Exception as e:
                pass
            # 아마 일어날일이 없을듯
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
        content = {
            "detail": "Enter correct Latitude and Longitude",
        }
        return Response(content, status.HTTP_400_BAD_REQUEST)


# User의 모든 playlists
class UserMusiclistRetrieveUpdateDestroy(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPlaylistSerializer
    permission_classes = (  # TODO 퍼미션 체크 확실히
        permissions.IsAuthenticated,
        # ObjectHasPermission,
        # ObjectIsRequestUser,
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
            if music_pks: # 콤마로 구분된 음악들을 넣는다
                music_pks = [pk.strip() for pk in music_pks.split(",") if pk]
                for music_pk in music_pks:
                    music = Music.objects.get(pk=music_pk)  # music find
                    pl.add_music(music=music)
            Playlist.objects.make_playlist_id()
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
        except Playlist.DoesNotExist as e:
            # 이것도 일어나지는 않을듯
            context = {
                "detail": "Enter Playlist Name",
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(user)
        context = {
            "detail": "Created",
            "data": serializer.data,
        }
        return Response(context, status=status.HTTP_202_ACCEPTED)

    # Playlist 삭제
    def put(self, request, *args, **kwargs):
        delete_playlists = request.data.get("delete_playlist", None)
        if not delete_playlists:
            context = {
                "detail": "Enter Playlist"
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        try:
            user = self.get_queryset().get(pk=kwargs["pk"])
        except User.DoesNotExist as e:
            context = {
                "detail": "User does not exist",
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        if delete_playlists:  # 리스트 삭제
            delete_playlists = [playlist.strip() for playlist in delete_playlists.split(",") if playlist]
            for playlist in delete_playlists:
                try:
                    Playlist.objects.get(pk=playlist).delete()
                except Playlist.DoesNotExist as e:
                    context = {
                        "detail": "PlayList Does Not Exist",
                    }
                    return Response(context, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    context = {
                        "detail": e,
                    }
                return Response(context, status=status.HTTP_404_NOT_FOUND)
            Playlist.objects.make_playlist_id()
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
        deleted_musics = request.data.get("music", None)
        if deleted_musics:
            try:
                # 삭제되던 중간에 에러 발생시의 처리?
                deleted_musics = [musics.strip() for musics in deleted_musics.split(",") if musics]
                pk = kwargs["pk"]
                playlist_pk = kwargs["playlist_pk"] # TODO id를 받는데 변수명은 pk 고치자
                playlist = Playlist.objects.prefetch_related("user").get(
                    user_id=pk, playlist_id=playlist_pk)
                for music_deleted in deleted_musics:
                    music = playlist.playlist_musics.filter(pk=music_deleted)
                    PlaylistMusics.objects.select_related("name_playlist").select_related("music").filter(
                        name_playlist__playlist_id=playlist_pk,
                        music=music,
                    ).delete()
                    # PlaylistMusics.objects.filter(
                    #     name_playlist__playlist_id=playlist_pk,
                    #     music=music,
                    # ).delete()
                    # if music_deleted:
                    #     music_deleted = music_deleted.strip()
                    #     music = playlist.playlist_musics.filter(pk=music_deleted)
                    #     PlaylistMusics.objects.filter(
                    #         name_playlist__playlist_id=playlist_pk,
                    #         music=music,
                    #     ).delete()
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
