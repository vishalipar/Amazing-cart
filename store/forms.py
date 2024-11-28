from django import forms
from .models import ReviewRating, Product

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']

class ProductUploadForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'images', 'stock', 'is_available', 'category']
        
    def __init__(self, *args, **kwargs):
        super(ProductUploadForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs['placeholder'] = 'Enter Product Name'
        
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'