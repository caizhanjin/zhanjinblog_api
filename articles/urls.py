from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'CollectionsModelViewSet', views.CollectionsModelViewSet, base_name='CollectionsModelViewSet')
router.register(r'ArticlesModelViewSet', views.ArticlesModelViewSet, base_name='ArticlesModelViewSet')
router.register(r'LabelsModelViewSet', views.LabelsModelViewSet, base_name='LabelsModelViewSet')
router.register(r'MessagesModelViewSet', views.MessagesModelViewSet, base_name='MessagesModelViewSet')
router.register(r'RecentModelViewSet', views.RecentModelViewSet, base_name='RecentModelViewSet')


urlpatterns = [
    url(r'^', include(router.urls)),
]

