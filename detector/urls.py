from django.urls import path
from . import views

urlpatterns = [
    path('register-page/', views.register_page, name='register-page'),
    path('register/',               views.register,           name='register'),
    path('profile/',                views.profile,            name='profile'),
    path('analyze-text/',           views.analyze_text,       name='analyze-text'),
    path('analyze-link/',           views.analyze_link,       name='analyze-link'),
    path('cyber-chat/',             views.cyber_chat,         name='cyber-chat'),

    # History — static paths BEFORE dynamic <int:id> paths
    path('history/',                views.history_list,       name='history-list'),
    path('history/all/delete/',     views.delete_all_history, name='history-delete-all'),
    path('history/<int:id>/',       views.history_detail,     name='history-detail'),
    path('history/<int:id>/delete/', views.delete_history,   name='history-delete'),
]