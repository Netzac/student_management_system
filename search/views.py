from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from bookstore.models import Book

def search(request):
	search = request.GET.get('q')
	books = Book.objects.all().order_by("id")
	if search:
		books = books.filter(
			Q(title__icontains=search)|Q(category__name__icontains=search)|Q(author__icontains=search)

		)

	paginator = Paginator(books, 10)
	page = request.GET.get('page')
	books = paginator.get_page(page)

	context = {
		"book": books,
		"search": search,
	}
	return render(request, 'bookstore/category.html', context)
