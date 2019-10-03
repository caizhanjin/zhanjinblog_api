from django.db import models

from units.base_model import BaseModel


class Image(BaseModel):
    """图片表"""
    image_info = models.ImageField(upload_to='img', verbose_name='图片地址')

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    def __str__(self):
        return self.id
