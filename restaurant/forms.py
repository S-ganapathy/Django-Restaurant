from django import forms
from .models import CUISINE_CHOICES, FOOD_TYPES,Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
SORT_CHOICES=[
    ('','Order by ...'),
    ('rating','Rating'),
    ('-rating','Rating (High to low)'),
    ('cost_of_two','Cost of two'),
    ('-cost_of_two','Cost of two (High to low)')
]

class RestaurantFilterForm(forms.Form):

    sort_by=forms.CharField(label='Sort',
                            required=False,
                            widget=forms.Select(choices=SORT_CHOICES))

    
     # Filter fields

    city=forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full','placeholder':'Enter City . . .','list':'city-list'})
     )
    
    food_type=forms.MultipleChoiceField(
        choices=FOOD_TYPES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-checkbox mt-1 block'})
    )

    cuisines=forms.MultipleChoiceField(
        choices=CUISINE_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class':'form-multiselect mt-1 block w-full','placeholder':'select or type cuisine'})
    )

    rating=forms.CharField(
        required=False,
        widget=forms.NumberInput(attrs={
            'min': 0, 'max': 5, 'step': 0.1, 'class': 'form-input mt-1 block w-full', 'placeholder': '0-5'
        })
    )

    cost_of_two=forms.CharField(
        required=False,
        widget=forms.NumberInput(attrs={
            'min': 0, 'max': 10000, 'step': 100, 'class': 'form-input mt-1 block w-full', 'placeholder': 'Enter cost (₹)'
        })
    )

    is_open=forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'form-checkbox mt-1 block'})
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model=Review
        fields=['rating','comment']
        widgets={
            'rating':forms.NumberInput(attrs={'min':1,'max':5,'step':0.5}),
            'comment':forms.Textarea(attrs={'placeholder':'Write your comment here . . .'}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username','first_name','email', 'password1', 'password2')