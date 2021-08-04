from django.urls import path

from . import views

app_name = "yWait"
urlpatterns = [ 
    path('',views.index, name = 'index'),
    path('location/<int:pk>/', views.LocationView.as_view(), name='viewLocation'),
    path('location/<int:pk>/update/', views.updatelocation, name='updateLocation'),
    path('location/create',views.LocationCreate.as_view(), name='createLocation'),
    path('location/<int:pk>/delete/',views.LocationDelete.as_view(), name='deleteLocation'),
    path('comparison/<int:pk>/', views.ComparisonView.as_view(), name='viewComparison'),
    path('comparison/<int:pk>/delete/', views.ComparisonDelete.as_view(), name='deleteComparison'),
    path('comparison/<int:pk>/update/', views.updateComparison, name='updateComparison'),
    path('comparison/create', views.ComparisonCreate.as_view(), name='createComparison'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('comparison/<int:pk>/modify', views.ComparisonModify.as_view(), name='modifyComparison')
  ]