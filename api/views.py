from django.http import JsonResponse
from api.serializers import ProductSerializer, OrderSerializer, ProductInfoSerializer, OrderCreateSerializer
from api.models import Product, Order,OrderItem

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import Max

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import viewsets

from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
    )

from api.filters import ProductFilter, InStockFilterBackend, OrderFilter #from filters.py module

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


# # function views
# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)

# @api_view(['GET'])
# def product_view(request, pk):
#     product = get_object_or_404(Product,pk=pk)
#     serializer = ProductSerializer(product)
#     return Response(serializer.data)
#class based views

# @api_view(['GET'])
# def order_list(request):
#     orders = Order.objects.prefetch_related(
#     'items__product'
#     ).all()
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)

# @api_view(['GET'])
# def product_info(request):
    # products = Product.objects.all()
    # serializer = ProductInfoSerializer({
    #     'products': products,
    #     'count': len(products),
    #     'max_price': products.aggregate(max_price=Max('price'))['max_price']
    # })
    # return Response(serializer.data)


class ProductListCreateAPIView(generics.ListCreateAPIView): # both GET and POST method
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer

    # filterset_fields = ('name', 'price') # view field filter

    filterset_class = ProductFilter

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
        ] # override default filter
    
    search_fields = ['name','description']
    ordering_filter = ['name','price','stock']

    pagination_class = LimitOffsetPagination
    # pagination_class = PageNumberPagination
    # pagination_class.page_size = 2
    # pagination_class.page_query_param = 'pagenum' #custom name
    # pagination_class.page_size_query_param ='size'
    # pagination_class.max_page_size = 6

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    

class ProductCreateAPIView(generics.CreateAPIView): # POST API method
    model = Product
    serializer_class = ProductSerializer

class ProductCreateAPIView(generics.ListAPIView): # GET API method
    model = Product
    serializer_class = ProductSerializer


class ProductDeatailAPIView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'pk' # custom primary key

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT','DELETE','PATCH']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    

class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer    
    permission_classes = [IsAuthenticated]
    pagination_class=None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self): # to choose serializer
        #can also check If post.request
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff: #not admin then
            return qs.filter(user=self.request.user)
        return qs



#class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer

# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated] # permisson checks to disable endpoint during dynamical filetering

#     def get_queryset(self): # dynamically filerting use this method
#         qs = super().get_queryset()  # all orders Model.objects.all()
#         return qs.filter(user=self.request.user)  # only orders of logged-in user



class ProductInfoAPIVIew(APIView): # not binded to model # mostly good for returing data like end point
    def get(self,request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)

 


