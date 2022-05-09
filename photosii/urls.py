from django.urls import path, include
from django.conf.urls.static import static

from .views import *
from .apps import PhotosiiConfig

app_name = PhotosiiConfig.name

urlpatterns = [
    path('account/', include('account.urls')),
    path('', homepage, name='homepage'),
    path('project_manager', project_manager, name='project_add'),
    path('projects/<int:pk>/edit', project_edit, name='project_edit'),
    path('projects/<int:pk>/delete', project_delete, name='project_delete'),
    path('create_dataset', photo_create_dataset, name='photo_create_dataset'),
    path('load', photo_load, name='photo_load'),
    path('<int:id>/delete', photo_delete, name='photo_delete'),
    path('<int:id>/', photo_view, name='photo_view'),
    path('api/<int:user_id>/photos/', PhotoListView.as_view()),
    path('api/<int:user_id>/photos/<int:pk>/', PhotoView.as_view()),
    path('api/<int:user_id>/photos/<int:pk>/delete/', PhotoDelete.as_view()),
    path('api/photos/post/train', PhotoPostTrain.as_view()),
    path('api/photos/post/prediction', PhotoPostPrediction.as_view()),
    path('api/<int:user_id>/tags/', TagsView.as_view()),
    path('api/<int:user_id>/tags/<int:tag_pk>/', TagView.as_view()),
    path('api/<int:user_id>/tags/<int:project_pk>/train/', StartTrain.as_view()),
    path('api/<int:user_id>/tags/<int:project_pk>/prediction/', StartPrediction.as_view()),
    path('api/users/', UsersView.as_view()),
    path('api/<int:user_id>/users/', UserView.as_view()),
    path('api/users/auth/', UserAuth.as_view()),
]
