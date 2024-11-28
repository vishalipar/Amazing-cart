from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetPassword_validate/<uidb64>/<token>/', views.resetPassword_validate, name='resetPassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # business
    path('login/business_login/', views.business_login, name='business_login'),
    path('business/dashboard/', views.business_dashboard, name='business_dashboard'),
    
    # enter business details
    path('business_detail/<int:user_id>/', views.business_detail, name='business_detail'),
    path('myproducts/', views.myproducts, name='myproducts'),
    path('upload_products/', views.upload_products, name='upload_products'),
    
    
    # path('business_register/', views.register, name='business_register'),
]
