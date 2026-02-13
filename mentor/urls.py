from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.users_list, name="users_list"),
    path("tasks/", views.tasks_list, name="tasks_list"),
    path("abi_talebe/", views.abi_talebe_wa_listesi, name="abi_talebe"),
    path("", views.dashboard, name="dashboard"),
    path("persons/", views.persons_list, name="persons_list"),
    path("persons/<int:pk>/", views.person_detail, name="person_detail"),

    path("groups/", views.groups_list, name="groups_list"),
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),

    path("packages/", views.packages_list, name="packages_list"),
    path("packages/<int:pk>/", views.package_detail, name="package_detail"),
    path("persons/create/", views.person_create, name="person_create"),
    path("groups/", views.groups_list, name="groups_list"),
    path("groups/create/", views.group_create, name="group_create"),
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),
    path("groups/<int:pk>/edit/", views.group_edit, name="group_edit"),
    
    path("packages/", views.packages_list, name="packages_list"),
    path("packages/create/", views.package_create, name="package_create"),
    path("packages/<int:pk>/", views.package_detail, name="package_detail"),
    path("packages/<int:pk>/edit/", views.package_edit, name="package_edit"),
    
]
