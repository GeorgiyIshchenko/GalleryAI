import json

from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser
from django.forms.models import model_to_dict

from rq import Queue
from redis import Redis

from django.core import serializers

from ai.functions import start_train, start_prediction


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(blank=True, null=True, max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Photo(models.Model):
    image = models.ImageField(upload_to='')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='photos', db_index=True, null=True,
                            blank=True)
    match = models.BooleanField(null=True, blank=True)
    device_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_tag = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pk} | {self.image}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.is_ai_tag and self.tag.photos.filter(
                Q(is_ai_tag=False) and Q(match=True)).count() >= 20 and self.tag.photos.filter(
            Q(is_ai_tag=False) and Q(match=False)).count() >= 20:
            if self.tag.is_trained:
                print('prediction has began')
                redis_conn = Redis()
                queue = Queue(connection=redis_conn)
                photo_query = self.tag.photos.filter(match=None)
                data = serializers.serialize('json', photo_query, fields=('image', 'tag'))
                print(data)
                job = queue.enqueue(start_prediction, data, self.tag.user.email)
            else:
                self.tag.is_trained = True
                self.tag.save()
                print('train has began')
                redis_conn = Redis()
                queue = Queue(connection=redis_conn)
                photo_query = self.tag.photos.filter(is_ai_tag=False)
                data = serializers.serialize('json', photo_query, fields=('image', 'match', 'tag'))
                job = queue.enqueue(start_train, data, self.tag.user.email)


    def get_absolute_url(self):
        return reverse('photosii:photo_view', kwargs={'id': self.id})

    def url_set_match(self):
        return reverse('photosii:photo_change_status', kwargs={'id': self.id, 'status': 'n'})

    def url_set_not_match(self):
        return reverse('photosii:photo_change_status', kwargs={'id': self.id, 'status': 'b'})

    class Meta:
        ordering = ('-created_at',)


class Tag(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='tags')
    name = models.CharField(max_length=64, default='default', unique=True)
    is_trained = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photos.filter(Q(is_ai_tag=False) and Q(match=True)).count() >= 20 and self.photos.filter(
                Q(is_ai_tag=False) and Q(match=False)).count() >= 20:
            self.is_trained = True

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('-name',)
