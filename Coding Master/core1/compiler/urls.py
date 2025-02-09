from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', views.home, name='home'),
    path('home_view/', views.home_view, name='home_view'),
    path('create/', views.create_contest_view, name='create_contest'),
    path('participate/<int:contest_id>/', views.participate_contest_view, name='participate_contest'),
    
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.view_profile, name='view_profile'),
    path('update/<int:pk>/', views.update_profile, name='update_profile'),
    path('delete/<int:pk>/', views.delete_profile, name='delete_profile'),
    
    path('leaderboard/', views.leaderboard_view, name='leaderboard_view'),
    path('profile/<str:username>/', views.view_user_profile, name='view_user_profile'),
    
    path('discussion/', views.discussion_view, name='discussion'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    
    path('home_question/', views.home_question_view, name='home_question'),
    path('create_question/', views.create_question_view, name='create_question'),
    path('participate_question/<int:question_id>/', views.participate_question_view, name='participate_question'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('compiler/', views.compiler_view, name='compiler'),
    path('delete-contest/<int:contest_id>/', views.delete_contest_view, name='delete_contest'),

    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_question_view/', views.admin_question_view, name='admin_question_view'),
    path('admin_delete/<int:question_id>/', views.delete_question_view, name='delete_question'),
    
    path('poll_create/', views.create_poll, name='create_poll'),
    path('poll/', views.display_polls, name='display_poll'),
    path('vote/<int:poll_id>/', views.vote_poll, name='vote_poll'),
    path('result/<int:poll_id>/', views.poll_result, name='poll_result'),
    path('delete_poll/<int:poll_id>/', views.delete_poll, name='delete_poll'),
    
    path('personal-space/', views.personal_space_view, name='personal_space'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('save-question/', views.save_question_to_folder, name='save_question_to_folder'),
    path('remove_question/', views.remove_question_from_folder, name='remove_question_from_folder'),
    path('delete_folder/', views.delete_folder, name="delete_folder"),
    
    path("submit-explanation/<int:question_id>/", views.submit_explanation, name="submit_explanation"),
    path("all-solutions/<int:question_id>/", views.all_solutions, name="all_solutions"),
    path("vote-explanation/<int:explanation_id>/<str:vote_type>/", views.vote_explanation, name="vote_explanation"),
    path('delete-explanation/<int:explanation_id>/', views.delete_explanation, name='delete_explanation'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

