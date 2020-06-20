from django.urls import path
from . import views

urlpatterns = [
    path('',views.firstpage),
    path('search/',views.search),
    path('search/DOC/<docId>',views.specificDOC),
]