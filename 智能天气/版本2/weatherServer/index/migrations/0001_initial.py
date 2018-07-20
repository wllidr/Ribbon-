# Generated by Django 2.0.3 on 2018-07-06 05:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accountName', models.CharField(max_length=100, verbose_name='用户名')),
                ('email', models.EmailField(max_length=254, verbose_name='用户邮箱')),
                ('suggestion', models.TextField(verbose_name='用户反馈意见')),
                ('dateTime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='反馈时间')),
            ],
            options={
                'verbose_name': '用户意见反馈',
                'verbose_name_plural': '用户意见反馈',
                'db_table': 'feedback',
            },
        ),
        migrations.CreateModel(
            name='SaveCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100, verbose_name='用户名')),
                ('vertificationCode', models.CharField(max_length=100, verbose_name='验证码')),
                ('dateTime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='反馈时间')),
            ],
            options={
                'verbose_name': '验证码信息存储',
                'verbose_name_plural': '验证码信息存储',
                'db_table': 'verticode',
            },
        ),
        migrations.CreateModel(
            name='SevenDayWeather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=20, verbose_name='城市')),
                ('date', models.CharField(max_length=40, verbose_name='日期')),
                ('day', models.CharField(max_length=20, verbose_name='日子')),
                ('temperature', models.CharField(max_length=30, verbose_name='温度')),
                ('weather', models.CharField(max_length=60, verbose_name='天气情况')),
                ('winddirection', models.CharField(max_length=60, verbose_name='风向')),
            ],
            options={
                'verbose_name': '7天气温情况',
                'verbose_name_plural': '7天气温情况',
                'db_table': 'weather',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=20, verbose_name='用户')),
                ('upwd', models.CharField(max_length=20, verbose_name='密码')),
                ('userCreateDate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('userUpdateDate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='修改时间')),
            ],
            options={
                'verbose_name': '用户信息',
                'verbose_name_plural': '用户信息',
                'db_table': 'user',
            },
        ),
    ]
