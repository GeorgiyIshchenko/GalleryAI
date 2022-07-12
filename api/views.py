from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status

from web.models import *

from .serializers import *
from .utils import check_token


class PhotoView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser,)

    def get(self, request, pk):
        photo = Photo.objects.get(id=pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data)


class StartTrain(APIView):

    def get(self, request, project_pk):
        print('api_train')
        project = Tag.objects.get(pk=project_pk)
        result = train(project)
        return Response({'success': result}, status=status.HTTP_201_CREATED)


class StartPrediction(APIView):

    def get(self, request, project_pk):
        print('api_prediction')
        project = Tag.objects.get(pk=project_pk)
        result = predict(project)
        return Response({'success': result}, status=status.HTTP_201_CREATED)


class PhotoPostTrain(APIView):

    def post(self, request):
        check_token(request)
        file_serializer = TrainSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoPostPrediction(APIView):

    def post(self, request):
        check_token(request)
        file_serializer = PredictionSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoDelete(APIView):

    def post(self, request, pk):
        check_token(request)
        Photo.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagsView(APIView):

    def post(self, request):

        user = check_token(request=request)
        tags = Tag.objects.filter(user=user).order_by('created_at')
        serializer = TagListSerializer(tags, many=True)

        return Response(serializer.data)


class TagView(APIView):

    def post(self, request, tag_pk):
        check_token(request)
        tag = Tag.objects.get(pk=tag_pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class UserView(APIView):

    def post(self, request):
        user = check_token(request)
        serializer = UserSerializer(user)
        return Response(serializer.data)
