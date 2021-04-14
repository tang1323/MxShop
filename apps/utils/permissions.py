from rest_framework import permissions


# 权限
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    # 这个obj是从数据库取出来的obj
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # SAFE_METHODS如果是安全的方法，那就返回True, 否则就判断是否同一个user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        # 这个obj是数据表里的models, 外键是user
        # 否则就判断是否同一个user
        return obj.user == request.user

















