
from email.policy import default
from django.db import models
#from django.contrib.auth.models import User
from student_core.models import CustomUser as User
from django.utils import timezone




class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Categories"

    def __str__(self):
        return str(f"{self.name}")


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete= models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Sub categories"

    def __str__(self):
        return str(f"{self.category} - {self.name}")

class Author(models.Model):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=150, unique=True ,db_index=True)
	bio = models.TextField()
	pic = models.FileField(upload_to = "Author/", null=True,blank=True)
	create_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.name




class Book(models.Model):
    sub_category = models.ForeignKey(Category, on_delete= models.CASCADE)
    isbn = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    author =models.ForeignKey(Author, on_delete = models.DO_NOTHING)
    publisher = models.CharField(max_length=250)
    date_published = models.DateTimeField()
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    price = models.IntegerField()
    stock = models.IntegerField()
    coverpage = models.FileField(upload_to = "Coverpage/" , null=True,blank=True)
    bookpage = models.FileField(upload_to = "Bookpage/", null=True,blank=True)

    totalreview = models.IntegerField(default=1)
    totalrating = models.IntegerField(default=5)

    class Meta:
        verbose_name_plural = "List of Books"

    def __str__(self):
        return self.title



class Review(models.Model):
	customer = models.ForeignKey(User, on_delete = models.CASCADE)
	book = models.ForeignKey(Book, on_delete = models.CASCADE)
	review_star = models.IntegerField()
	review_text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

class Slider(models.Model):
	title = models.CharField(max_length=150)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	slideimg = models.FileField(upload_to = "slide/")

	def __str__(self):
		return self.title
