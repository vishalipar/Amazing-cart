from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, type, password=None):
        if not email:
            raise ValueError('User must have an Email address')
        
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            type = type,
        )
        
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name= first_name,
            last_name= last_name,
        )
        
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user
    
# *
type_choices = [
    ('user', 'user'),
    ('business', 'business'),

]

class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    
    type = models.CharField(max_length=20, choices=type_choices, default='user')
    
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)
    is_superadmin = models.BooleanField(default = False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    
    objects = MyAccountManager()
    
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile', default=None)
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    
    def __str__(self):
        return self.user.first_name
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    
class BusinessDetails(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    bname = models.CharField(max_length=40)
    btype = models.CharField(max_length=40)
    baddress = models.CharField(max_length=40)
    bpostalcode = models.CharField(max_length=40)
    bcity = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    
    def __str__(self):
        return self.bname