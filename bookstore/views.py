from django.shortcuts import render, redirect, get_object_or_404
from requests import request

from .models import  Author, RequiredItem, Review, Slider
from .models import Category,SubCategory,Book,Stationery
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy,reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import  ReviewForm, StationeryForm, RequiredItemFormset

from student_core.models import CustomUser as User
from school.models import School

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

