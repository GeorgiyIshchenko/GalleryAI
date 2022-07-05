from abc import ABC

from rest_framework import serializers

from web.models import Photo, CustomUser, Tag


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username')


class UserAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50)


class PhotoListSerializer(serializers.ModelSerializer):
    tag = serializers.SlugRelatedField(slug_field='name', read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Photo
        fields = '__all__'


class PhotoJobSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Photo
        fields = ('image', 'status', 'user')


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('id', 'image', 'score', 'full_image', 'match', 'device_path', 'device_uri', 'created_at', 'is_ai_tag', 'tag')


class TagSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'is_trained', 'photos')


class TagListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'is_trained')


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('image', 'match', 'is_ai_tag', 'tag', 'device_path', 'device_uri')


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('image', 'tag', 'device_path', 'device_uri')