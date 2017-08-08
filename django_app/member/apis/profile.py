from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from member.serializers.profile import UserPasswordUpdateSerializers, UserListSerializers, \
    UserRetrieveUpdateDestroySerializers
from permissions import ObjectIsRequestUser

__all__ = (
    'UserRetrieveUpdateDestroyView',
    'UserPasswordUpdateView',
)

User = get_user_model()


class UserRetrieveUpdateDestroyView(APIView):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )
    lookup_field = ('pk',)

    # @staticmethod
    # def get_object(pk):
    #     try:
    #         return User.objects.get(pk=pk)
    #     except User.DoesNotExist:
    #         return Response(
    #             status=status.HTTP_404_NOT_FOUND
    #         )
    #
    # @staticmethod
    def get_object(self, pk):
        try:
            return User.objects.filter(pk=pk)
        except User.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    # retrieve
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserRetrieveUpdateDestroySerializers(
            user
        )
        return Response(serializer .data)

    # update
    def put(self, request, pk):
        # user = get_object_or_404(User, pk=pk)
        user = self.get_object(pk=pk)
        serializer = UserRetrieveUpdateDestroySerializers(
            user,
            request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # partial update
    def patch(self, request, pk):
        user = self.get_object(pk=pk)
        # user = get_object_or_404(User, pk=pk)
        # user = self.get_object(pk=pk)
        serializer = UserRetrieveUpdateDestroySerializers(
            user,
            request.data,
            partial=True
        )
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_400_BAD_REQUEST
        )

    # destroy
    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRetrieveUpdateDestroyView1(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializers
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )
    lookup_field = ('pk',)


class UserPasswordUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordUpdateSerializers
