from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, RecipeChallenge, Challenge
from .models import Recipe
from .models import Comment


# UserRegistrationForm: Custom form for registering new users, extending the built-in UserCreationForm
# and adding additional fields for a more detailed user profile.
class UserRegistrationForm(UserCreationForm):
    # Defines a first name field that is required for form submission.
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Defines a last name field that is required for form submission.
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Defines an email field that must be a valid email format and is required.
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    # The Meta class within a ModelForm is used to define certain properties of the form such as the model
    # it's associated with and the fields it should include.
    class Meta:
        # Links this form to the Django's default User model.
        model = User
        # Specifies the fields to be included in the form, ordering them as they should appear.
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        # Widgets adjust the display and functionality of certain fields.

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


# ProfileForm: A form to edit user's profile information like culinary preferences and dietary restrictions.
class ProfileForm(forms.ModelForm):
    # Meta class defines the model and fields that this form will interact with.
    class Meta:
        # Specifying the model with which the form interacts.
        model = Profile
        # Listing the fields from the Profile model that will be included in the form.
        fields = ['culinary_preferences', 'dietary_restrictions', 'image']
        # Widgets adjust the display and functionality of certain fields.
        widgets = {
            'culinary_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dietary_restrictions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# RecipeForm: A form for creating and updating Recipe instances, including detailed recipe information.
class RecipeForm(forms.ModelForm):
    # Meta class is where you provide meta-data to your ModelForm class.
    class Meta:
        # Specifying the model with which the form interacts.
        model = Recipe
        # Listing the fields from the Recipe model that will be included in the form.
        fields = ['title', 'description', 'ingredients', 'preparation_steps', 'preparation_time', 'images',
                  'status', 'calories', 'fat', 'carbs', 'proteins']
        # Widgets adjust the display and functionality of certain fields.
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control'}),
            'preparation_steps': forms.Textarea(attrs={'class': 'form-control'}),
            'preparation_time': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=Recipe.STATUS_CHOICES, attrs={'class': 'form-control'}),
            'calories': forms.TextInput(attrs={'class': 'form-control'}),
            'carbs': forms.TextInput(attrs={'class': 'form-control'}),
            'proteins': forms.TextInput(attrs={'class': 'form-control'}),
            'fat': forms.TextInput(attrs={'class': 'form-control'}),
            'images': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Initialize the form and inherit any initialization from the parent class.
        super(RecipeForm, self).__init__(*args, **kwargs)

        # Setting a custom label for the preparation time field to include the unit of measurement.
        self.fields['preparation_time'].label = "Preparation time (minutes)"

        # Adding units to the labels for the nutritional fields to guide user input.
        self.fields['calories'].label = "Calories (kcal per serving)"
        self.fields['fat'].label = "Fat (grams per serving)"
        self.fields['carbs'].label = "Carbohydrates (grams per serving)"
        self.fields['proteins'].label = "Proteins (grams per serving)"


# ChallengeForm: Form for creating or editing a cooking challenge.
class ChallengeForm(forms.ModelForm):
    # Meta class to link this form to the Challenge model and define the fields included in the form.
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'start_date', 'end_date', 'image']
        # Widgets are used to define HTML properties for the Django form fields.
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Initialize the form and apply custom settings for date fields.
        super(ChallengeForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        # Setting date and time input formats for the start and end date fields.
        self.fields['start_date'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['end_date'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['end_date'].widget.attrs['class'] = 'form-control'


# RecipeSubmissionForm: Form used for submitting a recipe to a challenge.
class RecipeSubmissionForm(forms.ModelForm):
    # Field to select a challenge; lists all challenges.
    challenge = forms.ModelChoiceField(queryset=Challenge.objects.all())
    # Field to select a recipe; initially empty, will be populated based on the user.
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.none())

    # Meta class linking this form to the RecipeChallenge model and defining which fields to include.
    class Meta:
        model = RecipeChallenge
        fields = ['challenge', 'recipe']

    def __init__(self, *args, **kwargs):
        # Extract user from keyword arguments and initialize the form.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter recipes to show only those created by the user, enhancing security and relevance.
        if user:
            self.fields['recipe'].queryset = Recipe.objects.filter(user=user)


# CommentForm: Form for creating comments on recipes.
class CommentForm(forms.ModelForm):
    # Meta class to specify the model and fields included in this form.
    class Meta:
        # Linking the form to the Comment model.
        model = Comment
        # Specifying which fields should be included in the form.
        fields = ['text']
        # Customizing the 'text' field to use a textarea with specific attributes.
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
