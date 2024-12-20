import requests
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct

from .forms import RegistrationForm, UserForm, UserProfileForm, BusinessDetailForm
from .models import Account, UserProfile, BusinessDetails
from store.models import Product

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            type = form.cleaned_data['type']
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password, type=type)
            user.phone_number = phone_number
            user.save()
            
            # USER ACTIVATION 
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/acount_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            if user.type == 'business':
                return redirect('/accounts/login/business_login/?command=verification&email='+email)
            
            return redirect('/accounts/login/?command=verification&email='+email)
        if not form.is_valid():
            print(form.errors)
    else:
        form = RegistrationForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        # for business accounts
        # print(user.type)
        
        # if user.type == 'business':
        #     return render(request, '')
            
            
        # *
        
        if user is not None:
            if user.type == 'user':
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        
                        # getting product_variation by cart id
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                            
                            # get the cart items from the user to access his product_variation
                            cart_item = CartItem.objects.filter(user=user)
                            ex_var_list = []
                            id = []
                            for item in cart_item:
                                existing_variation = item.variations.all()
                                ex_var_list.append(list(existing_variation))
                                id.append(item.id)
                            
                            # product_variation = [1,2,3,4,6]
                            # ex_var_list = [4,6,3,5]
                                
                            for pr in product_variation:
                                if pr in ex_var_list:
                                    index = ex_var_list.index(pr)
                                    item_id = id[index]
                                    item = CartItem.objects.get(id=item_id)
                                    item.quantity += 1
                                    item.user = user
                                    item.save()
                                else:
                                    cart_item = CartItem.objects.filter(cart=cart)
                                    for item in cart_item:
                                        item.user = user
                                        item.save()
                except:
                    pass
                auth.login(request, user)
                messages.success(request, "You are now logged in.")
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('dashboard')
            
            else:
                messages.error(request, "You registered as business account")
                return redirect('login')
            
            
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out.")
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,"Congratulations Your account is activated.")
        
        if user.type == 'business':
            # user = Account.objects.get(user=request.user)
            return redirect('business_detail', user.id)
        
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('register')
    
@login_required(login_url= 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    
    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=request.user)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            messages.success(request, "Password reset email has been sent to your email address")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist!")
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
        
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
            
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
    
    
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user = request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, "Password updated successfully.")
                return redirect('change_password')
            else:
                messages.error(request, "Please enter valid current password")
                return redirect('change_password')
        else:
            messages.error(request, "Password does not match!")
            return redirect('change_password')
            
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)



# business account creation
def business_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        
        if user is not None:
            if user.type == 'business':
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        
                        # getting product_variation by cart id
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                            
                            # get the cart items from the user to access his product_variation
                            cart_item = CartItem.objects.filter(user=user)
                            ex_var_list = []
                            id = []
                            for item in cart_item:
                                existing_variation = item.variations.all()
                                ex_var_list.append(list(existing_variation))
                                id.append(item.id)
                            
                            # product_variation = [1,2,3,4,6]
                            # ex_var_list = [4,6,3,5]
                                
                            for pr in product_variation:
                                if pr in ex_var_list:
                                    index = ex_var_list.index(pr)
                                    item_id = id[index]
                                    item = CartItem.objects.get(id=item_id)
                                    item.quantity += 1
                                    item.user = user
                                    item.save()
                                else:
                                    cart_item = CartItem.objects.filter(cart=cart)
                                    for item in cart_item:
                                        item.user = user
                                        item.save()
                except:
                    pass
                auth.login(request, user)
                messages.success(request, "Logged in as business account.")
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('business_dashboard')
            
            else:
                messages.error(request, "No business account found.")
                return redirect('business_login')
            
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('business_login')
            
    return render(request, 'accounts/business_login.html')

# def business_register(request):
#     return render(request, 'accounts/business_register.html')


# enter business details
def business_detail(request, user_id):
    user = Account.objects.get(pk=user_id)
    print(user.first_name)
    if request.method == 'POST':
        print(user.email)
        
        form = BusinessDetailForm(request.POST)
        if form.is_valid():
            details = form.save(commit=False)
            # details.user = user
            details.save()
        
    # if request.method == 'POST':
    #     bname = request.POST['bname']
    #     btype = request.POST['btype']
    #     baddress = request.POST['baddress']
    #     bpostalcode = request.POST['bpostalcode']
    #     bcity = request.POST['bcity']
    #     state = request.POST['state']
        
    #     details = BusinessDetails(user=user, bname=bname, btype=btype, baddress=baddress, bpostalcode=bpostalcode, bcity=bcity, state=state)
    #     details.save()
    
    context = {
        'user':user,
    }
    return render(request, 'business/business_detail.html', context)


def business_dashboard(request):
    return render(request, 'business/dashboard.html')


def myproducts(request):
    product = Product.objects.all()
    context = {
        'product':product,
    }
    return render(request, 'business/myproducts.html', context)


def upload_products(request):
    return render(request, 'business/upload_products.html')