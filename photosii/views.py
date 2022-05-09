from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status
from django.http import JsonResponse
from django.db import IntegrityError

from .models import *
from .forms import *
from .serializers import *

import json


def homepage(request):
    if request.user.is_authenticated:
        user = request.user
        if user.tags.count():
            tags = user.tags.all().order_by('created_at')
            print(tags)
            if request.GET.get('tag'):
                tag = tags.get(pk=int(request.GET.get('tag')))
                request.session['tag_id'] = tag.id
            else:
                try:
                    tag = Tag.objects.get(id=request.session['tag_id'])
                except KeyError:
                    tag = tags[0]
                except Tag.DoesNotExist:
                    tag = tags[0]
            match = tag.photos.filter(Q(match=True) & Q(is_ai_tag=True))
            not_match = tag.photos.filter(Q(match=False) & Q(is_ai_tag=True))
            trained_match = tag.photos.filter(Q(match=True) & Q(is_ai_tag=False))
            trained_not_match = tag.photos.filter(Q(match=False) & Q(is_ai_tag=False))
            random_photo = None
            if trained_match.count():
                random_photo = trained_match.order_by('?')[0]
            data = {f"Match ({match.count()})": {"color": "white", "text": "dark", "photos": match},
                    f"Don't match ({not_match.count()})": {"color": "dark", "text": "white", "photos": not_match}, }
            data_trained = {
                f"Match ({trained_match.count()})": {"color": "white", "text": "dark", "photos": trained_match},
                f"Don't match ({trained_not_match.count()})": {"color": "dark", "text": "white",
                                                               "photos": trained_not_match}, }
            return render(request, 'homepage.html',
                          {'data': data, 'data_trained': data_trained, 'dropdown': True, 'tags': tags,
                           'current_tag': tag, 'random_photo': random_photo})
        return render(request, 'homepage.html', {'dropdown': True, 'add_tag': True})
    return render(request, 'homepage.html')


def project_manager(request):
    projects = request.user.tags.all()
    if request.method == 'POST':
        user = request.user
        tag_name = request.POST.get('tag_name')
        try:
            new_project = Tag.objects.create(user=user, name=tag_name)
            new_project.save()
        except IntegrityError:
            print('ПРОЕКТ С ТАКИМ ИМЕНЕМ УЖЕ СУЩЕСТВУЕТ')
    return render(request, 'project_manager.html', {'projects': projects})


def project_edit(request, pk):
    if request.method == 'POST':
        project = Tag.objects.get(pk=pk)
        project.name = request.POST.get('project_name', project.name)
        project.save()
        return redirect(reverse('photosii:project_add'))


def project_delete(request, pk):
    project = Tag.objects.get(pk=pk)
    project.delete()
    return redirect(reverse('photosii:project_add'))


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
    if request.method == "POST":
        tag = Tag.objects.get(pk=int(request.POST.get('tag')))
        photos = request.FILES.getlist('photos')
        for i in photos:
            Photo.objects.create(image=i, tag=tag)
        predict(tag)
        return redirect('/')
    tags = request.user.tags.filter(is_trained=True)
    current_project = tags[0]
    if request.GET.get('project_id'):
        try:
            current_project = tags.get(id=request.GET['project_id'])
        except Tag.DoesNotExist:
            print('ТЭГ НЕ ОБУЧЕН')
    return render(request, 'photo_load.html', {'tags': tags, 'current_project': current_project})


def photo_create_dataset(request):
    if request.method == "POST":
        print(request.POST)
        tag = Tag.objects.get(pk=int(request.POST.get('tag')))
        match = request.FILES.getlist('match')
        doesnt_match = request.FILES.getlist('doesnt_match')
        for i in match:
            Photo.objects.create(image=i, match=True, tag=tag, is_ai_tag=False)
        for i in doesnt_match:
            Photo.objects.create(image=i, match=False, tag=tag, is_ai_tag=False)
        train(tag)
        return redirect('/')
    tags = request.user.tags.all()
    current_project = tags[0]
    if request.GET.get('project_id'):
        current_project = tags.get(id=request.GET['project_id'])
    form = DataSetCreationForm()
    return render(request, 'photo_create_dataset.html',
                  {'tags': tags, 'form': form, 'current_project': current_project})


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


class StartTrain(APIView):

    def get(self, request, user_id, project_pk):
        print('api_train')
        project = Tag.objects.get(pk=project_pk)
        result = train(project)
        return Response({'success': result}, status=status.HTTP_201_CREATED)


class StartPrediction(APIView):

    def get(self, request, user_id, project_pk):
        print('api_prediction')
        project = Tag.objects.get(pk=project_pk)
        result = predict(project)
        return Response({'success': result}, status=status.HTTP_201_CREATED)


class PhotoPostTrain(APIView):

    def post(self, request):
        file_serializer = TrainSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoPostPrediction(APIView):

    def post(self, request):
        file_serializer = PredictionSerializer(data=request.data)
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
        tags = Tag.objects.filter(user=user).order_by('created_at')
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
