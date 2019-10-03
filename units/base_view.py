from rest_framework import viewsets, status

from .format_data import ReturnData


class BaseModelViewSet(viewsets.ModelViewSet):
    """重写ModelViewSet，自定义返回值"""
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return ReturnData(code=201, msg=serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ReturnData(msg='创建成功', data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return ReturnData(data=serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return ReturnData(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return ReturnData(code=201, msg=serializer.errors)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ReturnData(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ReturnData(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ReturnData(msg='删除成功')


class WithCreateUserModelViewSet(BaseModelViewSet):
    """包含创建用户的模型基类"""
    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data['create_user_info'] = request.user.id

        serializer = self.get_serializer(data=request_data)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return ReturnData(code=201, msg=serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ReturnData(msg='创建成功', data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)
