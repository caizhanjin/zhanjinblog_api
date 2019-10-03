from django.db import models
from django.contrib.auth.models import User

from units.base_model import BaseModel, RelatedUserModel
from users.models import UserInfo


class Collections(RelatedUserModel):
    """文集表"""
    collect_name = models.CharField(unique=True, max_length=50, verbose_name="文集名称")
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="描述")
    read_count = models.IntegerField(default=0, verbose_name="阅读量", null=True, blank=True)

    class Meta:
        verbose_name = "文集"
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    def __str__(self):
        return self.id


class Labels(RelatedUserModel):
    """标签表"""
    label_name = models.CharField(unique=True, max_length=50, verbose_name="文章标签")

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    def __str__(self):
        return self.id


class Articles(RelatedUserModel):
    """文章表"""
    title = models.CharField(max_length=100, verbose_name="文章名称")
    author = models.CharField(max_length=50, verbose_name="文章作者")
    body = models.TextField(verbose_name="文章内容（markdown，包括标题）")
    read_count = models.IntegerField(default=0, verbose_name="阅读量", null=True, blank=True)
    # message_count = models.IntegerField(default=0, verbose_name="留言数", null=True, blank=True)
    collection_info = models.ForeignKey(Collections, on_delete=models.SET_NULL,
                                        null=True, blank=True, verbose_name="文章集合")
    collection_order = models.IntegerField(default=0, verbose_name='文集顺序', null=True, blank=True)
    labels_all = models.ManyToManyField(Labels, related_name="relate_articles_labels",
                                        verbose_name="文章标签")  # 至少一个标签
    original_link = models.URLField(verbose_name='原文链接', null=True, blank=True)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    def __str__(self):
        return self.id


class Messages(BaseModel):
    """留言表"""
    article_info = models.ForeignKey(Articles, on_delete=models.CASCADE, verbose_name="留言对应文章")
    nickname = models.CharField(max_length=50, verbose_name="用户昵称")
    email = models.EmailField(verbose_name="用户邮箱")
    message_body = models.TextField(verbose_name="留言内容")
    is_reply = models.BooleanField(default=False, verbose_name="是否回复留言")
    reply_nickname = models.CharField(max_length=50, null=True, blank=True, verbose_name="回复留言的用户昵称")
    reply_id = models.ForeignKey("self", on_delete=models.CASCADE,
                                 null=True, blank=True, verbose_name="回复留言楼主的ID")  # 自关联,非必填
    is_author = models.BooleanField(default=False, verbose_name="是否是作者留言")

    class Meta:
        verbose_name = "留言"
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    def __str__(self):
        return self.id


class Recent(BaseModel):
    """博主近况/动态"""
    recent_info = models.CharField(max_length=500, verbose_name='博主动态详情')
    create_user_info = models.ForeignKey(UserInfo, on_delete=models.PROTECT, verbose_name='创建用户')

    class Meta:
        verbose_name = "近况"
        verbose_name_plural = verbose_name
        ordering = ('-create_time', )

    def __str__(self):
        return self.id
