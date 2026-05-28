from django import forms
from .models import Equipment
from .models import Review

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['title', 'category', 'equipment_type', 'model', 'year',
                 'hours_worked', 'price', 'region', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year < 1900 or year > 2026:
            raise forms.ValidationError('Год должен быть в диапазоне 1900–2026.')
        return year

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Цена должна быть положительной.')
        return price

class ContactSellerForm(forms.Form):
    name = forms.CharField(max_length=100, label='Ваше имя')
    email = forms.EmailField(label='Email')
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Сообщение'
    )

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
