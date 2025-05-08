from django.urls import path 
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('products/',views.ProductListCreateAPIView.as_view()),
    path('products/<int:pk>',views.ProductDeatailAPIView.as_view()),
    path('products/info',views.ProductInfoAPIVIew.as_view()),

]

router =DefaultRouter()
router.register('order',views.OrderViewset)
urlpatterns += router.urls