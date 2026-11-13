from django.urls import path

from . import views

urlpatterns = [
    path("", views.board, name="board"),
    path("requests/", views.request_list, name="request_list"),
    path("new/", views.new_request, name="new_request"),
    path("requests/<int:pk>/", views.detail, name="detail"),
    path("requests/<int:pk>/attachments/", views.upload_attachment, name="upload_attachment"),
    path("attachments/<int:pk>/", views.download_attachment, name="download_attachment"),
    path("schedule/", views.schedule, name="schedule"),
    path("notifications/", views.notifications, name="notifications"),
]
