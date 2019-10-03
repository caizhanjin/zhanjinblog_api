from rest_framework import viewsets, views, status
from rest_framework.decorators import action

from .models import Articles, Collections, Labels, Messages, Recent
from .serializers import ArticlesSerializer, CollectionsSerializer, LabelsSerializer, MessagesSerializer, RecentSerializer

from units.base_view import BaseModelViewSet, WithCreateUserModelViewSet
from units.format_data import ReturnData, PageInfo
from units.permission import IsAdminUserOrReadOnly, get_look_permission_array


class ArticlesModelViewSet(WithCreateUserModelViewSet):
    queryset = Articles.objects.all()
    serializer_class = ArticlesSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data['create_user_info'] = request.user.id
        if not request_data.get('author', ''):
            request_data['author'] = request.user.username
        # 如存在文集，获取顺序，默认为(文集数量+1)
        collection_info = request_data.get('collection_info', '')
        if collection_info:
            collection_count = self.queryset.filter(collection_info=collection_info).count()
            request_data['collection_order'] = collection_count + 1

        serializer = self.get_serializer(data=request_data)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return ReturnData(code=201, msg=serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ReturnData(msg='创建成功', data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        request_data = request.data
        # 如作者字段为空，则填充编辑用户
        if not request_data.get('author', ''):
            request_data['author'] = request.user.username
        # 如文集发生改变，则调整顺序
        collection_info = request_data.get('collection_info', '')

        instance = self.get_object()
        # queryset_slice = self.queryset.filter(id=kwargs.get('pk')).first()
        if collection_info != '' and collection_info != instance.collection_info_id:
            collection_count = self.queryset.filter(collection_info=collection_info).count()
            request_data['collection_order'] = collection_count + 1

        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return ReturnData(code=201, msg=serializer.errors)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return ReturnData(data=serializer.data)

    @action(methods=['put'], detail=False)
    def change_collection_order(self, request, *args, **kwargs):
        """列表更新，文章顺序"""
        article_id_array = request.data
        article_count = len(article_id_array)
        for item_key in range(article_count):
            result_update = self.update_only_order(id=article_id_array[item_key],
                                                   collection_order=(article_count-item_key))
            if not result_update:
                return ReturnData(code=201, msg='更新id %s 文章顺序失败' % article_id_array[item_key])

        return ReturnData()

    def update_only_order(self, **kwargs):
        """执行单个文章顺序更新"""
        update_data = kwargs

        partial = kwargs.pop('partial', True)
        instance = self.queryset.filter(id=update_data.get('id')).first()
        serializer = self.get_serializer(instance, data=update_data, partial=partial)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return False

        self.perform_update(serializer)

        return True

    @action(methods=['get'], detail=False)
    def get_detail(self, request, *args, **kwargs):
        request_data = request.query_params
        article_id = request_data.get('id', '')
        if not article_id:
            return ReturnData(code=201, msg='缺少文章id')

        queryset_article = Articles.objects.filter(id=article_id). \
            select_related('collection_info'). \
            prefetch_related('messages_set').first()

        if not queryset_article:
            return ReturnData(code=201, msg='查找不到对应文章')

        detail_data = {}
        detail_data['id'] = queryset_article.id
        detail_data['body'] = queryset_article.body
        detail_data['title'] = queryset_article.title
        detail_data['author'] = queryset_article.author
        detail_data['create_time'] = queryset_article.create_time
        detail_data['update_time'] = queryset_article.update_time
        detail_data['original_link'] = queryset_article.original_link
        detail_data['read_count'] = queryset_article.read_count

        detail_data['collection_id'] = '' if not queryset_article.collection_info else queryset_article.collection_info.id

        if queryset_article.collection_info:
            collection_info = {
                'collection_id': queryset_article.collection_info.id,
                'collection_name': queryset_article.collection_info.collect_name,
            }
            detail_data['collection_info'] = collection_info
        else:
            detail_data['collection_info'] = {}

        message_set = queryset_article.messages_set.order_by('-create_time').filter(is_reply=False)

        if message_set:
            detail_data['message_set'] = []
            detail_data['message_count'] = queryset_article.messages_set.all().count()
            for item_message in message_set:
                slice_message = {}
                slice_message['id'] = item_message.id
                slice_message['create_time'] = item_message.create_time
                slice_message['nickname'] = item_message.nickname
                slice_message['email'] = item_message.email
                slice_message['message_body'] = item_message.message_body
                slice_message['is_author'] = item_message.is_author

                slice_message['reply_set'] = []
                reply_set = item_message.messages_set.order_by('create_time')
                if reply_set:
                    for item_reply in reply_set:
                        slice_reply = {}
                        slice_reply['id'] = item_reply.id
                        slice_reply['create_time'] = item_reply.create_time
                        slice_reply['nickname'] = item_reply.nickname
                        slice_reply['email'] = item_reply.email
                        slice_reply['message_body'] = item_reply.message_body
                        slice_reply['is_author'] = item_reply.is_author
                        slice_reply['reply_nickname'] = item_reply.reply_nickname
                        slice_message['reply_set'].append(slice_reply)

                detail_data['message_set'].append(slice_message)

        else:
            detail_data['message_set'] = []
            detail_data['message_count'] = 0

        return ReturnData(data=detail_data)

    @action(methods=['get'], detail=False)
    def get_by_label(self, request, *args, **kwargs):
        """通过标签获取文章列表"""
        request_data = request.query_params
        look_permission_array = get_look_permission_array(user_info=request.user)

        if request_data.get('label_id', ''):
            article_array = list(Labels.objects.filter(id=request_data.get('label_id')).values_list('relate_articles_labels__id', flat=True))
            if request_data.get('order_by', '') == 'read_count':
                queryset_article = Articles.objects.order_by('-read_count'). \
                    filter(visible_permission__in=look_permission_array, id__in=article_array)
            else:
                queryset_article = Articles.objects.filter(visible_permission__in=look_permission_array,
                                                           id__in=article_array)
        else:
            if request_data.get('order_by', '') == 'read_count':
                queryset_article = Articles.objects.order_by('-read_count') \
                    .filter(visible_permission__in=look_permission_array)
            else:
                queryset_article = Articles.objects.filter(visible_permission__in=look_permission_array)

        queryset_article.select_related('collection_info'). \
            prefetch_related('labels_all')

        # 分页
        page_info, slice_data = PageInfo(total=queryset_article.count(),
                                         page_size=int(request_data.get('page_size', 10)),
                                         current_index=int(request_data.get('current_index', 1)))
        queryset_article = queryset_article[slice_data[0]:slice_data[1]]

        list_data = []
        for item_article in queryset_article:
            slice_data = {}
            slice_data['id'] = item_article.id
            slice_data['title'] = item_article.title
            slice_data['read_count'] = item_article.read_count
            slice_data['create_time'] = item_article.create_time
            slice_data['update_time'] = item_article.update_time
            slice_data['visible_permission'] = item_article.visible_permission
            slice_data['message_count'] = item_article.messages_set.count()

            if item_article.collection_info:
                article_count = item_article.collection_info.articles_set. \
                    filter(visible_permission__in=look_permission_array).count()
                first_article_obj = item_article.collection_info.articles_set.order_by('-collection_order'). \
                    filter(visible_permission__in=look_permission_array).first()
                collection_info = {
                    'collection_id': item_article.collection_info.id,
                    'collection_name': item_article.collection_info.collect_name,
                    'article_count': article_count,
                    'first_article_id': first_article_obj.id,
                }
                slice_data['collection_info'] = collection_info
            else:
                slice_data['collection_info'] = {}

            queryset_label = item_article.labels_all.filter(visible_permission__in=look_permission_array)
            slice_data['article_set'] = []
            for item_label in queryset_label:
                slice_label = {}
                slice_label['id'] = item_label.id
                slice_label['label_name'] = item_label.label_name
                slice_data['article_set'].append(slice_label)

            list_data.append(slice_data)

        return ReturnData(data={'page_info': page_info, 'list_data': list_data})

    @action(methods=['get'], detail=False)
    def get_by_collection(self, request, *args, **kwargs):
        request_data = request.query_params
        look_permission_array = get_look_permission_array(user_info=request.user)

        collection_id = request_data.get('collection_id', '')
        if not collection_id:
            return ReturnData(code=201, msg='缺少文集id')

        queryset_article = Articles.objects. \
            filter(visible_permission__in=look_permission_array,
                   collection_info__id=collection_id). \
            order_by('-collection_order')

        list_data = []
        for item_article in queryset_article:
            slice_data = {}
            slice_data['id'] = item_article.id
            slice_data['title'] = item_article.title

            list_data.append(slice_data)

        list_dict = {}
        len_list_data = len(list_data)
        for item_key in range(len_list_data):
            slice_dict = list_data[item_key].copy()
            slice_dict['prev_id'] = '' if item_key == 0 else list_data[(item_key-1)]['id']
            slice_dict['next_id'] = '' if (item_key+1) == len_list_data else list_data[(item_key+1)]['id']

            list_dict[list_data[item_key]['id']] = slice_dict

        data_info = {
            'list_data': list_data,
            'list_dict': list_dict
        }

        return ReturnData(data=data_info)

    @action(methods=['get'], detail=False)
    def add_read_count(self, request, *args, **kwargs):
        """阅读量加1，权限问题，用get"""
        request_data = request.query_params
        if not request_data.get('id', ''):
            return ReturnData(status='201', msg='文章id不能为空')

        instance = self.queryset.filter(id=request_data.get('id')).first()
        update_data = {'read_count': instance.read_count+1}
        partial = update_data.pop('partial', True)

        serializer = self.get_serializer(instance, data=update_data, partial=partial)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return False

        self.perform_update(serializer)
        return ReturnData()


class CollectionsModelViewSet(WithCreateUserModelViewSet):
    queryset = Collections.objects.all()
    serializer_class = CollectionsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    @action(methods=['get'], detail=False)
    def get_permission_list(self, request, *args, **kwargs):
        """获取文集列表，根据用户角色不同展示不同数据"""
        look_permission_array = get_look_permission_array(user_info=request.user)

        queryset_collection = Collections.objects.order_by('-read_count'). \
            filter(visible_permission__in=look_permission_array). \
            prefetch_related('articles_set')

        list_data = []
        for item_collection in queryset_collection:
            slice_data = {}
            slice_data['id'] = item_collection.id
            slice_data['collect_name'] = item_collection.collect_name
            slice_data['description'] = item_collection.description
            slice_data['read_count'] = item_collection.read_count
            # 文集数据量少，可以这样用；数据量大需要考虑查询速度问题
            slice_data['article_count'] = item_collection.articles_set. \
                filter(visible_permission__in=look_permission_array).count()
            first_article_id = ''
            if slice_data['article_count'] != 0:
                first_article_obj = item_collection.articles_set.order_by('-collection_order'). \
                    filter(visible_permission__in=look_permission_array).first()
                first_article_id = first_article_obj.id
            slice_data['first_article_id'] = first_article_id

            list_data.append(slice_data)

        return ReturnData(data=list_data)

    @action(methods=['get'], detail=False)
    def add_read_count(self, request, *args, **kwargs):
        """阅读量加1，权限问题，用get"""
        request_data = request.query_params
        if not request_data.get('id', ''):
            return ReturnData(status='201', msg='文集id不能为空')

        instance = self.queryset.filter(id=request_data.get('id')).first()
        update_data = {'read_count': instance.read_count+1}
        partial = update_data.pop('partial', True)

        serializer = self.get_serializer(instance, data=update_data, partial=partial)
        is_valid = serializer.is_valid(raise_exception=False)
        if not is_valid:
            return False

        self.perform_update(serializer)
        return ReturnData()


class LabelsModelViewSet(WithCreateUserModelViewSet):
    queryset = Labels.objects.all()
    serializer_class = LabelsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    @action(methods=['get'], detail=False)
    def get_permission_list(self, request, *args, **kwargs):
        """获取标签列表，根据用户角色不同展示不同数据"""
        look_permission_array = get_look_permission_array(user_info=request.user)

        queryset_label = Labels.objects. \
            filter(visible_permission__in=look_permission_array)

        list_data = []
        for item_label in queryset_label:
            slice_data = {}
            slice_data['id'] = item_label.id
            slice_data['label_name'] = item_label.label_name
            list_data.append(slice_data)

        return ReturnData(data=list_data)


class MessagesModelViewSet(BaseModelViewSet):
    queryset = Messages.objects.all()
    serializer_class = MessagesSerializer


class RecentModelViewSet(BaseModelViewSet):
    queryset = Recent.objects.all()
    serializer_class = RecentSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

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

    @action(methods=['get'], detail=False)
    def get_recent_data(self, request, *args, **kwargs):
        """获取最近一条动态"""
        recent_data = self.queryset.first()
        serializer = self.get_serializer(recent_data)

        return ReturnData(data=serializer.data)


