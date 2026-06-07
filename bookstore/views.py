from django.shortcuts import render, redirect, get_object_or_404
from requests import request

from .models import  Author, RequiredItem, Review, Slider
from .models import Category,SubCategory,Book,Stationery
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Sum

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy,reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import  ReviewForm, StationeryForm, RequiredItemFormset

from student_core.models import CustomUser as User, Students
from school.models import School

from.utils import get_teacher_cls_id

# Create your views here.
def index(request):
    active_books = Book.objects.filter(status='1', delete_flag=0).select_related('category')
    categories = Category.objects.filter(status='1', delete_flag=0).order_by('name')
    try:
        newpublished = active_books.order_by('-date_created')[:15]
        slide = Slider.objects.order_by('-created')[:3]
    except:
        newpublished = []
        slide = []

    try:
        from order.models import OrderItem
        top_selling_ids = (
            OrderItem.objects.values('book')
            .annotate(sold=Sum('quantity'))
            .order_by('-sold')[:10]
        )
        sales_by_book = {item['book']: item['sold'] for item in top_selling_ids}
        top_selling_books = list(active_books.filter(id__in=sales_by_book.keys()))
        top_selling_books.sort(key=lambda book: sales_by_book.get(book.id, 0), reverse=True)
    except:
        sales_by_book = {}
        top_selling_books = []

    if not top_selling_books:
        top_selling_books = list(active_books.order_by('-totalrating', '-totalreview')[:10])

    low_stock_books = active_books.filter(stock__gt=0, stock__lte=5).order_by('stock', 'title')[:6]
    featured_books = active_books.filter(stock__gt=0).order_by('-totalrating', '-date_created')[:8]
    category_cards = (
        categories.annotate(book_count=Count('book'))
        .filter(book_count__gt=0)
        .order_by('-book_count', 'name')[:6]
    )
    book_count = active_books.count()
    in_stock_count = active_books.filter(stock__gt=0).count()
    out_of_stock_count = active_books.filter(stock__lte=0).count()
    review_count = Review.objects.count()
    total_stock = active_books.aggregate(total=Sum('stock'))['total'] or 0

    try:
        cart_items = len(request.session.get('cart', {}))
    except:
        cart_items = 0

    context = {
        "newbooks":newpublished,
        "slide": slide,
        "categories": categories,
        "category_cards": category_cards,
        "featured_books": featured_books,
        "top_selling_books": top_selling_books,
        "low_stock_books": low_stock_books,
        "sales_by_book": sales_by_book,
        "store_stats": {
            "book_count": book_count,
            "in_stock_count": in_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "review_count": review_count,
            "total_stock": total_stock,
        },
        "cart_items": cart_items,
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




class StationeryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Stationery
    form_class = StationeryForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("store:stationery-list")
    success_message = "New Item successfully added"


class StationeryListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Stationery
    template_name = "stationery_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StationeryForm()
        return context

class StationeryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Stationery
    fields = ["item","desc"]
    success_url = reverse_lazy("store:stationery-list")
    success_message = "Stationery successfully updated."
    template_name = "hod_template/mgt_form.html"


class StationeryDeleteView(LoginRequiredMixin, DeleteView):
    model = Stationery
    success_url = reverse_lazy("store:stationery-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "Item {} has been deleted with its attachment"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.type)
        messages.success(self.request, self.success_message.format(obj.type))
        return super(StationeryDeleteView, self).delete(request, *args, **kwargs)

    
from django.contrib.auth.decorators import login_required
from student_core.models import Courses

@login_required
def select_item_class(request):
    classes = Courses.objects.all()
    students=None
    
    user_type = request.user.user_type
    classes = Courses.objects.all()

    if user_type=='2':
        classes= classes.filter(id=get_teacher_cls_id(request))
    if request.method == "POST":
        data = request.POST
        #clsid=0
        try:
        
            clsid = data['classes']
            #classes = Courses.objects.all().filter(id=clsid)
        #students = Student.objects.filter(course_id=clsid)
        except:
            # classes = Courses.objects.all()
            #return redirect('select-result-class')
            cls_id=0
        return redirect('store:requireditem-create', clsid=clsid)

    return render(request, 'select_class.html', {'class':classes})

''' RI for RequiredItem'''
class RICreateView(SuccessMessageMixin,LoginRequiredMixin, CreateView):
    model= RequiredItem
    #fields=['staff_id','cls_id']
    form_class = RequiredItemFormset
    template_name="bookstore/requireditem_form.html"
    error_message ="Item format not allowed"
    success_message = 'Item successfully added.'
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clsid"] = self.kwargs['clsid']
        return context
    
    def get(self,*args,**kwargs):
        # staffs = Staffs.objects.all().values('id')
        # classes = Courses.objects.all().values('id'),initial={"item":"","cls": clsid,"session":self.request.current_session_id,"qty":1}
        clsid=self.kwargs['clsid']
        cls = get_object_or_404(Courses,id=clsid)
        formset=RequiredItemFormset(queryset=RequiredItem.objects.filter(cls = clsid))
        print("clsid", cls.id)
        return self.render_to_response({"requireditem_formset":formset,"cls": cls})

    def post(self,*args,**kwargs):
        clsid=self.kwargs['clsid']
        cls = get_object_or_404(Courses,id=clsid)
        formset=RequiredItemFormset(data=self.request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(reverse_lazy("store:requireditem-list"))
        return self.render_to_response({"requireditem_formset":formset,"cls": cls})
  
class RIListView(ListView):

    model=RequiredItem
    template_name="bookstore/requireditem_list.html"

    def get_context_data(self, **kwargs):
        sch = School.objects.first()
        context = super().get_context_data(**kwargs)
        context["school"] = sch
        return context
    
    def get_queryset(self):
        user_type = self.request.user.user_type
        if user_type=='1':
            return RequiredItem.objects.all()
        elif user_type=='2':
            return RequiredItem.objects.filter(cls=get_teacher_cls_id(self.request))
        elif user_type=='3':
            return RequiredItem.objects.filter(cls=self.request.user.students.course_id)
            

class RIUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = RequiredItem
    fields=['item','qty']
    #form_class = RequiredItemFormset
    success_url = reverse_lazy("store:requireditem-list")
    success_message = "Item successfully updated."

    
   # template_name = "hod_template/mgt_form.html"



class RIDeleteView(LoginRequiredMixin, DeleteView):
    model = RequiredItem
    success_url = reverse_lazy("store:requireditem-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"
