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
        match = user.photos.filter(status='n')
        not_match = user.photos.filter(status='b')
        data = {f"Match ({match.count()})": {"color": "#30d5c8", "photos": match},
                f"Don't match ({not_match.count()})": {"color": "#a04de5", "photos": not_match}}
        return render(request, 'homepage.html', {'data': data, 'search_input': True})
    else:
        return render(request, 'homepage.html')


def photo_view(request, id):
    photo = get_object_or_404(Photo, id=id)
    if request.method == "POST":
        photo.status = request.POST['status']
        photo.save()
    return render(request, 'photo_view.html', {'photo': photo})


def photo_delete(request, id):
    photo = get_object_or_404(Photo, id=id)
    photo.delete()
    return redirect('/')


def photo_add(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            return redirect('/')
        else:
            print(form.errors)
    form = PhotoForm()
    return render(request, 'photo_add.html', {'form': form})


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
        print(user.photos.all())
        data = [{"name": "Match", "photos": PhotoListSerializer(user.photos.filter(status='n'), many=True).data},
                {"name": "Doesn't Match",
                 "photos": PhotoListSerializer(user.photos.filter(status='b'), many=True).data}]
        print(data)
        return Response(data)


class TagView(APIView):

    def get(self, request, user_id, tag_name):
        user_photos = Photo.objects.filter(user=user_id)
        tag = Tag.objects.get(name=tag_name)
        data = dict()
        data["name"] = tag_name
        data["photos"] = PhotoSerializer(user_photos.filter(tag=tag), many=True).data
        return Response(data)


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
