from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status

from web.models import *
from .serializers import *


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

    def get(self, request, user_id, pk):
        Photo.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


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