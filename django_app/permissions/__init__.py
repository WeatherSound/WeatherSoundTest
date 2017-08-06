from rest_framework import permissions


# 객체 자체가 요청자인지 확인하는 인증 클래스 정의
class ObjectIsRequestUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
