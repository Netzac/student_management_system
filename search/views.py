from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from bookstore.models import Book, Category, Author

def search(request):
	search = request.GET.get('q')
	books = Book.objects.all()
	if search:
		books = books.filter(
			Q(title__icontains=search)|Q(sub_category__name__icontains=search)|Q(author__name__icontains=search)

		)

	paginator = Paginator(books, 10)
	page = request.GET.get('page')
	books = paginator.get_page(page)

	context = {
		"book": books,
		"search": search,
	}
	return render(request, 'bookstore/category.html', context)
