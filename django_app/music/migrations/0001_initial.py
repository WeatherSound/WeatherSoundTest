# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 06:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_music', models.CharField(max_length=256)),
                ('time_music', models.PositiveSmallIntegerField(default=0)),
                ('source_music', models.CharField(max_length=256)),
                ('name_music', models.CharField(max_length=100)),
                ('name_artist', models.CharField(max_length=100)),
                ('name_album', models.CharField(blank=True, max_length=100)),
                ('sunny', models.PositiveIntegerField(default=0, verbose_name='맑음')),
                ('foggy', models.PositiveIntegerField(default=0, verbose_name='안개')),
                ('rainy', models.PositiveIntegerField(default=0, verbose_name='비')),
                ('cloudy', models.PositiveIntegerField(default=0, verbose_name='흐림')),
                ('snowy', models.PositiveIntegerField(default=0, verbose_name='눈')),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_playlist', models.CharField(default='playlist', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistMusics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('music', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.Music')),
                ('name_playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.Playlist')),
            ],
        ),
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=100)),
                ('time_saved', models.DateTimeField(auto_now_add=True)),
                ('cur_weather', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='playlist',
            name='playlist_musics',
            field=models.ManyToManyField(related_name='playlist_musics', through='music.PlaylistMusics', to='music.Music'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
