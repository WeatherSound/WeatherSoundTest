from django.contrib.auth import get_user_model
from rest_framework import generics

from member.serializers.profile import UserPasswordUpdateSerializers

__all__ = (
    'UserPasswordUpdateView',
)


User = get_user_model()


class UserPasswordUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordUpdateSerializers

