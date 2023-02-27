from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
	path('', views.index, name = "index"),
	path('book/<int:id>', views.get_book, name="book"),
	path('books', views.get_books, name="books"),
   
	path('category/<int:id>', views.get_book_category, name="category"),
	path('author/<int:id>', views.get_author, name = "author"),
    
    
    path("stationery/list/", views.StationeryListView.as_view(), name="stationery-list"),
    path("stationery/create", views.StationeryCreateView.as_view(), name="stationery-create"),
    path("stationery/<int:pk>/update/", views.StationeryUpdateView.as_view(), name="stationery-update"),
    path("stationery/<int:pk>/delete/", views.StationeryDeleteView.as_view(),name="stationery-delete"),
    
     #URLS for Requireditems
    path('requireditem_class/', views.select_item_class, name="requireditem-class"),
    path('required_items/<clsid>', views.RICreateView.as_view(), name="requireditem-create"),
    path('requireditems/', views.RIListView.as_view(), name="requireditem-list"),
    path("requireditems/<int:pk>/update/", views.RIUpdateView.as_view(), name="requireditem-update"),
    path("requireditems/<int:pk>/delete/", views.RIDeleteView.as_view(), name="requireditem-delete"),

]
