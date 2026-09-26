from django.urls import path

from ticket_mail import views

urlpatterns = [
    path("connect/", views.connect, name="ticket_mailbox_connect"),
    path("callback/", views.callback, name="ticket_mailbox_callback"),
]
