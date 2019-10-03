from rest_framework.permissions import BasePermission

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsAdminUserOrReadOnly(BasePermission):
    """
    管理员具有全部权限，否则只读
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


def get_look_permission_array(user_info=None):
    if user_info.is_anonymous:
        # 匿名用户，即没有登录用户
        return [4]
    elif user_info.is_superuser:
        # 超级用户
        return [1, 2, 3, 4]
    elif user_info.is_staff:
        # 管理员
        return [2, 3, 4]
    else:
        # 普通用户
        return [3, 4]