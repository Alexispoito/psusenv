from django.contrib import admin
from django.urls import path
from studentorg.views import HomePageView, OrganizationList
from studentorg import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.HomePageView.as_view(), name='home'),
    path('organization_list', OrganizationList.as_view(), name='organization-list'),
]