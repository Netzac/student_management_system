from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.http import JsonResponse
from student_core.models import CustomUser as  User
from django.contrib import messages
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .pdfcreator import renderPdf

from django.views.decorators.csrf import csrf_exempt

def order_create(request):
	cart = Cart(request)

	if request.user.is_authenticated:
		
		customer = get_object_or_404(User, id=request.user.id)
		form = OrderCreateForm(request.POST or None, initial={"name": customer.first_name, "email": customer.email, "phone": customer.students.parent_contact_number,"address":customer.students.address})
		
		if request.method == 'POST':
			
			if form.is_valid():
				order = form.save(commit=False)
				order.customer = User.objects.get(id=request.user.id)
				order.payable = cart.get_total_price()
				order.totalbook = len(cart) # len(cart.cart) // number of individual book


				order.save()

				for item in cart:
					OrderItem.objects.create(
						order=order, 
						book=item['book'], 
						price=item['price'], 
						quantity=item['quantity']
						)
				cart.clear()
				return render(request, 'order/successfull.html', {'order': order})

			else:
				messages.error(request, "Fill out your information correctly.")

		if len(cart) > 0:
			print('Generating order...')
			return render(request, 'order/order.html', {"form": form})
		else:
			return redirect('store:books')
	else:
		return redirect('store:signin')
			
def order_list(request):
	my_order = Order.objects.filter(customer_id = request.user.id).order_by('-created')
	paginator = Paginator(my_order, 5)
	page = request.GET.get('page')
	myorder = paginator.get_page(page)

	return render(request, 'order/list.html', {"myorder": myorder})

def order_details(request, id):
	order_summary = get_object_or_404(Order, id=id)

	if order_summary.customer_id != request.user.id:
		return redirect('store:index')

	orderedItem = OrderItem.objects.filter(order_id=id)
	context = {
		"o_summary": order_summary,
		"o_item": orderedItem
	}
	return render(request, 'order/details.html', context)

class pdf(View):
    def get(self, request, id):
        try:
            query=get_object_or_404(Order,id=id)
        except:
            Http404('Content not found')
        context={
            "order":query
        }
        article_pdf = renderPdf('order/pdf.html',context)
        return HttpResponse(article_pdf,content_type='application/pdf')


def confirm_order(request,pk):
	order_obj = get_object_or_404(Order,id=pk)
	return render(request, 'order/successfull.html', {'order': order_obj})
    
from paystackapi.transaction import Transaction
import json
@csrf_exempt
def verify_online_payment(request,ref,amount):
    #redirect_url = reverse('receipt-create')
	response = Transaction.verify(reference=str(ref))
	print("response: ",response,ref)
	cart = Cart(request)
	customer = get_object_or_404(User, id=request.user.id)
	init_data = {"name": customer.first_name, "email": customer.email, "phone": customer.students.parent_contact_number,"address":customer.students.address}
	form = Order(**init_data)
	id = 1
	if form:
		order = form
		order.customer = User.objects.get(id=request.user.id)
		order.payable = amount
		order.transaction_id = str(ref)
		order.totalbook = len(cart) # len(cart.cart) // number of individual book
		order.paid =True
		order.save()
		id = order.id
		for item in cart:
			OrderItem.objects.create(
				order=order, 
				book=item['book'], 
				price=item['price'], 
				quantity=item['quantity']
			)
	list_data ={"id": id}
	cart.clear()
	print('jsaon data', json.dumps(list_data),list_data)
	return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
	#return render(request, 'order/successfull.html', {'order': order})
    #return redirect('order:order_create')