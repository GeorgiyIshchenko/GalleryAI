from .models import Photo, Tag


def train_result(id, success):
    tag = Tag.objects.get(id=id)
    if success:
        tag.is_trained = True
    else:
        tag.is_trained = False
    tag.save()


def prediction_result(data):
    for id in data.keys():
        photo = Photo.objects.get(id=id)
        photo.is_ai_tag = True
        if data[id]:
            photo.match = True
        else:
            photo.match = False
        photo.save()