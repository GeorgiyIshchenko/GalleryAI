import json
import os
import time
import asyncio

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

from PIL import Image, ImageOps

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


def gen_image_filename(instance, filename):
    return '{0}/{1}/{2}/{3}'.format(instance.tag.user.email, instance.tag.name,
                                    "match" if instance.match else "not_match", filename)


def gen_image_filename_full(instance, filename):
    return '{0}/{1}/{2}/{3}'.format(instance.tag.user.email, instance.tag.name,
                                    "match" if instance.match else "not_match", "full_" + filename)


class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to=gen_image_filename)
    full_image = models.ImageField(upload_to=gen_image_filename_full, null=True, blank=True)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='photos', db_index=True, null=True,
                            blank=True)
    score = models.IntegerField(null=True, blank=True)
    match = models.BooleanField(null=True, blank=True)
    device_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_tag = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pk} | {self.image}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.full_image:
            full_image = ContentFile(self.image.read())
            new_picture_name = self.image.name.split("/")[-1]
            self.full_image.save(new_picture_name, full_image)
            image = Image.open(self.image.path)
            if image.width > 512 or image.height > 512:
                image.thumbnail((512, 512))
                image = ImageOps.exif_transpose(image)
                image.save(self.image.path)

    def get_absolute_url(self):
        return reverse('photosii:photo_view', kwargs={'id': self.id})

    def url_set_match(self):
        return reverse('photosii:photo_change_status', kwargs={'id': self.id, 'status': 'n'})

    def url_set_not_match(self):
        return reverse('photosii:photo_change_status', kwargs={'id': self.id, 'status': 'b'})

    class Meta:
        ordering = ('-created_at',)


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


@receiver(models.signals.post_delete, sender=Photo)
def delete_file(sender, instance, *args, **kwargs):
    if instance.image:
        _delete_file(instance.image.path)
    if instance.full_image:
        _delete_file(instance.full_image.path)


class Tag(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='tags')
    name = models.CharField(max_length=64, default='default', unique=True)
    is_trained = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    def get_random_photo(self):
        trained_match = self.photos.filter(Q(match=True) & Q(is_ai_tag=False))
        if trained_match.count():
            random_photo = trained_match.order_by('?')[0]
            return random_photo

    def get_absolute_url_edit(self):
        return reverse('photosii:project_edit', kwargs={'pk': self.id})

    def get_absolute_url_delete(self):
        return reverse('photosii:project_delete', kwargs={'pk': self.id})

    def get_path_dir_match(self):
        if self.photos.filter(match=True).count():
            return '/'.join(self.photos.filter(match=True)[0].image.url.split('/')[0:-1])

    def get_path_dir_not_match(self):
        if self.photos.filter(match=False).count():
            return '/'.join(self.photos.filter(match=False)[0].image.url.split('/')[0:-1])

    class Meta:
        ordering = ('name',)


def train(tag):
    if tag.photos.filter(Q(is_ai_tag=False) and Q(match=True)).count() >= 20 and tag.photos.filter(
            Q(is_ai_tag=False) and Q(match=False)).count() >= 20:
        photos = tag.photos.filter(is_ai_tag=False)
        data = serializers.serialize('json', photos)
        email = tag.user.email

        redis_conn = Redis()
        queue = Queue(connection=redis_conn)
        job = queue.enqueue(start_train, data, email)

        while not job.is_finished:
            job.refresh()
            time.sleep(1)

        tag.is_trained = True
        tag.save()
        return True
    return False


def predict(tag):
    if tag.is_trained:
        photo_query = tag.photos.filter(match=None)
        if photo_query.count() > 0:
            data = serializers.serialize('json', photo_query)
            email = tag.user.email

            redis_conn = Redis()
            queue = Queue(connection=redis_conn)
            job = queue.enqueue(start_prediction, data, email)

            while not job.is_finished:
                job.refresh()
                time.sleep(1)

            for photo_id in job.result.keys():
                photo = Photo.objects.get(id=photo_id)
                photo.is_ai_tag = True
                if job.result[photo_id]:
                    photo.match = True
                else:
                    photo.match = False
                photo.save()
        return True
    return False
