from django.urls import path, include

from .views import *
from .apps import ApiConfig

app_name = ApiConfig.name

urlpatterns = [
    path('<int:user_id>/photos/', PhotoListView.as_view()),
    path('<int:user_id>/photos/<int:pk>/', PhotoView.as_view()),
    path('<int:user_id>/photos/<int:pk>/delete/', PhotoDelete.as_view()),
    path('photos/post/train', PhotoPostTrain.as_view()),
    path('photos/post/prediction', PhotoPostPrediction.as_view()),
    path('<int:user_id>/tags/', TagsView.as_view()),
    path('<int:user_id>/tags/<int:tag_pk>/', TagView.as_view()),
    path('<int:user_id>/tags/<int:project_pk>/train/', StartTrain.as_view()),
    path('<int:user_id>/tags/<int:project_pk>/prediction/', StartPrediction.as_view()),
    path('users/', UsersView.as_view()),
    path('<int:user_id>/users/', UserView.as_view()),
    path('users/auth/', UserAuth.as_view()),
]