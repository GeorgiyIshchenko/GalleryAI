import json

from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser

from rq import Queue
from redis import Redis

from django.core import serializers

from ai.Functions import start_train


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(blank=True, null=True, max_length=150)
    is_trained = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Photo(models.Model):
    statuses = (
        ('n', 'Подходящая'),
        ('b', 'Не подходящая'),
    )

    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='photos')
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=statuses, default='n')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='photos', db_index=True, null=True,
                            blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_tag = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pk} | {self.image}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        user = self.user
        user.save()
        if not self.is_ai_tag and user.photos.filter(
                Q(is_ai_tag=False) and Q(status='n')).count() >= 10 and user.photos.filter(
                Q(is_ai_tag=False) and Q(status='b')).count() >= 10:
            print('education has began')
            redis_conn = Redis()
            queue = Queue(connection=redis_conn)
            photo_query = user.photos.filter(is_ai_tag=False)
            data = serializers.serialize('json', photo_query, fields=('image', 'status', 'user'))
            print(data)
            job = queue.enqueue(start_train, data)
            print('task has been sent')

    def get_absolute_url(self):
        return reverse('photosii:photo_view', kwargs={'id': self.id})

    def url_set_match(self):
        return reverse('photosii:photo_change_status', kwargs={'id': self.id, 'status': 'n'})

    def url_set_not_match(self):
        return reverse('photosii:photo_change_status', kwargs={'id': self.id, 'status': 'b'})

    def is_good(self):
        return self.status == 'n'

    class Meta:
        ordering = ('-created_at',)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, default='default', unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('-name',)
