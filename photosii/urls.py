from django.urls import path, include
from django.conf.urls.static import static

from .views import *
from .apps import PhotosiiConfig

app_name = PhotosiiConfig.name

urlpatterns = [
    path('account/', include('account.urls')),
    path('', homepage, name='homepage'),
    path('photo_add', photo_add, name='photo_add'),
    path('<int:id>/delete', photo_delete, name='photo_delete'),
    path('<int:id>/', photo_view, name='photo_view'),
    path('api/<int:user_id>/photos/', PhotoListView.as_view()),
    path('api/<int:user_id>/photos/<int:pk>/', PhotoView.as_view()),
    path('api/<int:user_id>/photos/<int:pk>/delete', PhotoDelete.as_view()),
    path('api/photos/post/', PhotoPost.as_view()),
    path('api/<int:user_id>/tags/', TagsView.as_view()),
    path('api/<int:user_id>/tags/<str:tag_name>', TagView.as_view()),
    path('api/users/', UsersView.as_view()),
    path('api/<int:user_id>/users/', UserView.as_view()),
    path('api/users/auth/', UserAuth.as_view()),
]
