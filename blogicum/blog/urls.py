from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.HomePage.as_view(), name='index'),
    path('posts/<int:pk>/edit/', views.UpdatePost.as_view(), name='edit_post'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>',
         views.UpdateComment.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>',
         views.DeleteComment.as_view(), name='delete_comment'),
    path('posts/<int:pk>/delete/', views.DeletePost.as_view(),
         name='delete_post'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/create/', login_required(views.PostCreate.as_view()),
         name='create_post'),
    path('category/<slug:category_slug>/', views.category_posts,
         name="category_posts"),
    path('profile/edit_profile/', login_required(views.EditProfile.as_view()),
         name='edit_profile'),
    path('profile/<slug:username>/', views.user_profile, name='profile'),
]
