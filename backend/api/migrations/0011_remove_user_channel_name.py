# Generated by Django 4.2.5 on 2024-03-09 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_user_followers_user_followings_delete_follower'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='channel_name',
        ),
    ]