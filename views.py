from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import hashlib              # for generating hash
from .models import Product
from .forms import ProductForm
import segno                # for generating qr code
import os
from django.http import HttpRequest

_INDEX_PAGE = 'index.html'
_LOGIN_PAGE = 'login.html'
_REGISTER_PAGE = 'register.html'
_USER_HOME_PAGE = 'userhome.html'
_ADMIN_HOME_PAGE = 'adminhome.html'
_ADD_PRODUCT_PAGE = 'addproduct.html'
_EDIT_PRODUCT_PAGE = 'editproduct.html'

_ADMIN_USERNAME = 'admin@gmail.com'
_ADMIN_PASSWORD = 'admin'


def index(req):
    if req.user.is_authenticated:
        if req.user.is_superuser:
            return redirect('adminhome')
        else:
            return redirect('userhome')
    return render(req, _INDEX_PAGE)


def login_user(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        if username == _ADMIN_USERNAME and password == _ADMIN_PASSWORD:
            user = authenticate(req, username='admin', password='admin')
            login(req, user)
            return redirect('adminhome')
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            return redirect('userhome')
        else:
            messages.error(req, 'Invalid username or password',
                           extra_tags='alert alert-danger')
            return render(req, _LOGIN_PAGE)
    return render(req, _LOGIN_PAGE)


# method to register user
def register_user(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        c_password = req.POST['confirm_password']
        name = req.POST['name']
        if password != c_password:
            messages.error(req, 'Password does not match',
                           extra_tags='alert alert-danger')
            return render(req, _REGISTER_PAGE)
        if User.objects.filter(username=username).exists():
            messages.error(req, 'Username already exists',
                           extra_tags='alert alert-danger')
            return render(req, _REGISTER_PAGE)
        user = User.objects.create_user(
            username=username, email=username, password=password, first_name=name)
        user.save()
        messages.success(req, 'User registered successfully',
                         extra_tags='alert alert-success')
        return render(req, _LOGIN_PAGE)
    return render(req, _REGISTER_PAGE)

# user home page
def user_home(req):
    if req.user.is_authenticated:
        return render(req, _USER_HOME_PAGE, {"products": Product.objects.all()})
    return redirect('index')

# method to add product


def add_product(req):
    form = ProductForm()
    if req.method == 'POST':
        form = ProductForm(req.POST, req.FILES)
        if form.is_valid():
            form.save(commit=False)
            hashed_id = hashlib.sha256(
                str(form.instance.toJson()).encode()).hexdigest()
            qr = segno.make(
                f'{hashed_id}\n fake' if form.instance.fake else f'{hashed_id}\n original')
            path = os.path.join(os.getcwd(), 'app', 'static',
                                'images', f'{hashed_id}.png')
            qr.save(path, scale=10)
            form.instance.image = f'{hashed_id}.png'
            form.save()
            messages.success(req, 'Product added successfully',
                             extra_tags='alert alert-success')
            return redirect('adminhome')
        else:
            return render(req, _ADD_PRODUCT_PAGE, {"form": form})
    return render(req, _ADD_PRODUCT_PAGE, {"form": form})


# method to delete product
def delete_product(req, id):
    if req.user.is_authenticated:
        product = Product.objects.get(id=id)
        product.delete()
        messages.success(req, 'Product deleted successfully',
                         extra_tags='alert alert-success')
        return redirect('adminhome')
    return redirect('index')


# method to update product
def update_product(req, id):
    product = Product.objects.get(id=id)
    form = ProductForm(instance=product)
    if req.method == 'POST':
        form = ProductForm(req.POST, req.FILES, instance=product)
        if form.is_valid():
            form.save(commit=False)
            hashed_id = hashlib.sha256(
                str(form.instance.toJson()).encode()).hexdigest()
            qr = segno.make(
                f'{hashed_id}\n fake' if form.instance.fake else f'{hashed_id}\n original')
            path = os.path.join(os.getcwd(), 'app', 'static',
                                'images', f'{hashed_id}.png')
            qr.save(path, scale=10)
            form.instance.image = f'{hashed_id}.png'
            form.save()
            messages.success(req, 'Product updated successfully',
                             extra_tags='alert alert-success')
            return redirect('adminhome')
        else:
            return render(req, _EDIT_PRODUCT_PAGE, {"form": form})
    return render(req, _EDIT_PRODUCT_PAGE, {"form": form})

# admin home page


def admin_home(req):
    if req.user.is_authenticated:
        return render(req, _ADMIN_HOME_PAGE, {"products": Product.objects.all()})
    return redirect('index')

# method to logout user


def logout_user(req):
    if req.user.is_authenticated:
        logout(req)
    return redirect('index')
