from django.urls import path
from . import views

urlpatterns = [
    path("refund-request/", views.create_refund_request),
    path("requests/", views.list_requests),
    path("customers/", views.list_customers),
]