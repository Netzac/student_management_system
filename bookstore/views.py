from django.shortcuts import render, redirect, get_object_or_404

from .models import  Author, Review, Slider
from .models import Category,SubCategory,Book
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import  ReviewForm

from student_core.models import CustomUser as User

# Create your views here.
def index(request):
    try:
        newpublished = Book.objects.order_by('-date_created')[:15]
        slide = Slider.objects.order_by('-created')[:3]
    except:
        newpublished = []
        slide = []

    context = {
        "newbooks":newpublished,
        "slide": slide
    }
    return render(request, 'bookstore/dashboard.html', context)



def payment(request):
    return render(request, 'bookstore/payment.html')


def get_book(request, id):
    form = ReviewForm(request.POST or None)
    book = get_object_or_404(Book, id=id)
    rbooks = Book.objects.filter(id=book.category.id)
    r_review = Review.objects.filter(book_id=id).order_by('-created')

    paginator = Paginator(r_review, 4)
    page = request.GET.get('page')
    rreview = paginator.get_page(page)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if form.is_valid():
                temp = form.save(commit=False)
                temp.customer = User.objects.get(id=request.user.id)
                temp.book = book          
                temp = Book.objects.get(id=id)
                temp.totalreview += 1
                temp.totalrating += int(request.POST.get('review_star'))
                form.save()  
                temp.save()

                messages.success(request, "Review Added Successfully")
                form = ReviewForm()
        else:
            messages.error(request, "You need login first.")
    context = {
        "book":book,
        "rbooks": rbooks,
        "form": form,
        "rreview": rreview
    }
    return render(request, "bookstore/book.html", context)


def get_books(request):
    books_ = Book.objects.all().order_by('-date_created')
    paginator = Paginator(books_, 10)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, "bookstore/category.html", {"book":books})

def get_book_category(request, id):
    book_ = Book.objects.filter(id=id)
    paginator = Paginator(book_, 10)
    page = request.GET.get('page')
    book = paginator.get_page(page)
    return render(request, "bookstore/category.html", {"book":book})

def get_author(request, id):
    wrt = get_object_or_404(Author, id=id)
    book = Book.objects.filter(author_id=wrt.id)
    context = {
        "wrt": wrt,
        "book": book
    }
    return render(request, "bookstore/author.html", context)
