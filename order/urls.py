from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
	path('', views.order_list, name="order_list"),
	path('<int:id>', views.order_details, name="order_details"),
	path('shipping/', views.order_create, name="order_create"),
    path('confirm/order/<int:pk>/', views.confirm_order, name="order_confirm"),
	path('pdf/<int:id>',views.pdf.as_view(), name="pdf"),
    
    
    path("ajax/order/verify-online-payment/<ref>/<amount>/",views.verify_online_payment,name="verify-online-payment")
]