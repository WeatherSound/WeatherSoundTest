from rest_framework import generics

from music.permissions import IsOwnerOrReadOnly
from .models import Music
from .serializers import MusicSerializer


class MusicListView(generics.ListCreateAPIView):
    queryset = Music.objects.all()
    serializer_class = MusicSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save(owner=self.request.user)
