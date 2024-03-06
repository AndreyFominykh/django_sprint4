from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('posts/<int:id>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/edit_comment/',
         views.edit_comment, name='edit_comment'),
    path('<int:post_id>/delete_comment/',
         views.delete_comment, name='delete_comment'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),
    path('<int:pk>/edit', views.PostUpdateView.as_view(), name='edit_post',),
    path('profile/<slug:username>/',
         views.UserDetailView.as_view(), name='profile'),
    path('edit_profile/<slug:username>/edit',
         views.ProfileUpdateView.as_view(), name='edit_profile'),
]
