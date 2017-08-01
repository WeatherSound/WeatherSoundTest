from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Music
from music.permissions import IsOwnerOrReadOnly
from music.serializers import MusicSerializer

__all__ = (
    'MusicListCreateView',
    'MusicListView',

)


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
    queryset = Music.objects.all()
    serializer_class = MusicSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save(owner=self.request.user)
