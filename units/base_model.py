from django.db import models

from users.models import UserInfo


class BaseModel(models.Model):
    """基础模型"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="逻辑删除")

    class Meta:
        # 为抽象模型类，用于其他模型来继承，数据库迁移时不会创建ModelBase表
        abstract = True


class RelatedUserModel(BaseModel):
    """基础模型，外键连用户表，权限管理使用"""
    # 超级管理员全部可见
    PERMISSION_CHOICES = (
        (1, "超级管理员可见"),
        (2, "管理员可见"),
        (3, "普通用户可见"),
        (4, "所有人可见"),
    )
    create_user_info = models.ForeignKey(UserInfo, on_delete=models.PROTECT, verbose_name="创建用户", default='')
    visible_permission = models.SmallIntegerField(choices=PERMISSION_CHOICES,
                                                  default=4, verbose_name="可见权限")

    class Meta:
        abstract = True
