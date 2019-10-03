from django.db import models

from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """用户表，继承框架自带"""
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号码")
    # role = models.SmallIntegerField() # 角色
    # icon = models.ImageField(upload_to="image/%Y/%m", default="image/default.png", max_length=100)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        ordering = ('-date_joined',)

    def __str__(self):
        return self.id


