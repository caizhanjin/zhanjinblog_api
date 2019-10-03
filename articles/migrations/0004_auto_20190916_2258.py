# Generated by Django 2.2.4 on 2019-09-16 14:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0003_auto_20190908_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='articles',
            name='create_user_info',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='创建用户'),
        ),
        migrations.AddField(
            model_name='articles',
            name='original_link',
            field=models.URLField(blank=True, null=True, verbose_name='原文链接'),
        ),
        migrations.AddField(
            model_name='articles',
            name='visible_permission',
            field=models.SmallIntegerField(choices=[(1, '超级管理员可见'), (2, '管理员可见'), (3, '普通用户可见'), (4, '所有人可见')], default=4, verbose_name='可见权限'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='message_count',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='留言数'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='read_count',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='阅读量'),
        ),
        migrations.AlterField(
            model_name='collections',
            name='create_user_info',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='创建用户'),
        ),
        migrations.AlterField(
            model_name='collections',
            name='visible_permission',
            field=models.SmallIntegerField(choices=[(1, '超级管理员可见'), (2, '管理员可见'), (3, '普通用户可见'), (4, '所有人可见')], default=4, verbose_name='可见权限'),
        ),
        migrations.AlterField(
            model_name='labels',
            name='create_user_info',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='创建用户'),
        ),
        migrations.AlterField(
            model_name='labels',
            name='visible_permission',
            field=models.SmallIntegerField(choices=[(1, '超级管理员可见'), (2, '管理员可见'), (3, '普通用户可见'), (4, '所有人可见')], default=4, verbose_name='可见权限'),
        ),
    ]
