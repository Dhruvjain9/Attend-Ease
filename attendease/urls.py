#attendease - urls

from django.contrib import admin
from django.urls import path, include
from attendance import views as attendance_views  # import views with alias
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # default auth urls
    path('login/', auth_views.LoginView.as_view(), name='login'),

    # Attendance app URLs
    path('attendance/', include('attendance.urls')),  # include all attendance app urls   
]
