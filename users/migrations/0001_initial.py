# Generated by Django 5.1.4 on 2024-12-10 19:06

import django.contrib.gis.db.models.fields
import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.CharField(max_length=9, validators=[django.core.validators.RegexValidator(message='Field must contain exactly 9 digits', regex='^\\d{9}$')])),
                ('name', models.CharField(max_length=50, null=True)),
                ('number', models.CharField(max_length=30, null=True)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('type', models.CharField(choices=[('user', 'User'), ('admin', 'Admin')], default='user', max_length=30)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('is_signed_up', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
    ]
