from django.urls import path, include
from . import views
urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.loginUser, name='login'),
    path('register', views.register, name='register'),
    path('token', views.token_send, name="token_send"),
    path('success', views.success, name="success"),
    path('verify/<auth_token>', views.verify, name="verify"),
    path('error', views.error, name="error"),
    path('logout', views.logoutUser, name="logout")
]