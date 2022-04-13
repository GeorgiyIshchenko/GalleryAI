from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status
from django.http import JsonResponse

from .models import *
from .forms import *
from .serializers import *

import json


def homepage(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            tag_name = request.POST.get('tag_name')
            new_tag = Tag.objects.create(user=user, name=tag_name)
            new_tag.save()
        if user.tags.count():
            tags = user.tags.all()
            if request.GET.get('tag'):
                tag = tags.get(pk=int(request.GET.get('tag')))
            else:
                tag = tags[0]
            match = tag.photos.filter(match=True)
            not_match = tag.photos.filter(match=False)
            data = {f"Match ({match.count()})": {"color": "#30d5c8", "photos": match},
                    f"Don't match ({not_match.count()})": {"color": "#a04de5", "photos": not_match}}
            return render(request, 'homepage.html', {'data': data, 'dropdown': True, 'tags': tags, 'current_tag': tag})
        return render(request, 'homepage.html', {'dropdown': True, 'add_tag': True})
    return render(request, 'homepage.html')


def photo_view(request, id):
    photo = get_object_or_404(Photo, id=id)
    if request.method == "POST":
        photo.match = (request.POST['match'] == "True")
        photo.save()
    return render(request, 'photo_view.html', {'photo': photo})


def photo_delete(request, id):
    photo = get_object_or_404(Photo, id=id)
    photo.delete()
    return redirect('/')


def photo_load(request):
    if request.method=="POST":
        tag = Tag.objects.get(pk=int(request.POST.get('tag')))
        photos = request.FILES.getlist('photos')
        for i in photos:
            photo = Photo.objects.create(image=i, tag=tag)
            photo.save()
        return redirect('/')
    tags = request.user.tags.filter(is_trained=True)
    return render(request, 'photo_load.html', {'tags': tags})


def photo_create_dataset(request):
    if request.method == "POST":
        print(request.POST)
        tag = Tag.objects.get(pk=int(request.POST.get('tag')))
        match = request.FILES.getlist('match')
        doesnt_match = request.FILES.getlist('doesnt_match')
        for i in match:
            photo = Photo.objects.create(image=i, match=True, tag=tag, is_ai_tag=False)
            photo.save()
        for i in doesnt_match:
            photo = Photo.objects.create(image=i, match=False, tag=tag, is_ai_tag=False)
            photo.save()
        return redirect('/')
    tags = request.user.tags.all()
    form = DataSetCreationForm()
    return render(request, 'photo_create_dataset.html', {'tags': tags, 'form': form})


class PhotoListView(APIView):

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        try:
            photos = Photo.objects.filter(user=user)
            serializer = PhotoListSerializer(photos, many=True)
            return Response(serializer.data)
        except:
            return Response("User does not exist", status=status.HTTP_200_OK)


class PhotoView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser,)

    def get(self, request, user_id, pk):
        photo = Photo.objects.get(id=pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data)


class PhotoPost(APIView):

    def post(self, request):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoDelete(APIView):

    def delete(self, request, pk):
        return Response(Photo.objects.get(pk=pk).delete())


class TagsView(APIView):

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        tags = Tag.objects.filter(user=user)
        serializer = TagListSerializer(tags, many=True)
        return Response(serializer.data)


class TagView(APIView):

    def get(self, request, user_id, tag_pk):
        tag = Tag.objects.get(pk=tag_pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class UsersView(APIView):

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)


class UserView(APIView):

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserAuth(APIView):

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer['email'].value
            password = serializer['password'].value
            user = authenticate(email=email, password=password)
            print(user)
            if user is not None:
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "Неправильный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
