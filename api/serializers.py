from rest_framework import serializers

from web.models import Photo, CustomUser, Tag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username')


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=50)


class PhotoJobSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Photo
        fields = ('image', 'status', 'user')


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('id', 'image', 'score', 'full_image', 'match', 'device_path', 'device_uri', 'created_at', 'is_ai_tag',
                  'tag')


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
