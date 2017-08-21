from rest_framework import permissions


# 객체 자체가 요청자인지 확인하는 인증 클래스 정의
class ObjectIsRequestUser(permissions.BasePermission):
    def has_permission(self, request, view):
        pass

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


# 객체의 소유자와 요청 유저가 같을 시에만 작동
class ObjectHasPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
