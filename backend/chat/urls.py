from django.urls import path,include
from . import views

urlpatterns = [
    path('groups/',views.GroupApiView.as_view()),
    path('pv/',views.PrivateRoomView.as_view()),
    
    
]
