from rest_framework import serializers

from .models import Photo, CustomUser, Tag


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
    tag = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Photo
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('image', 'description', 'status', 'user', 'is_ai_tag')
