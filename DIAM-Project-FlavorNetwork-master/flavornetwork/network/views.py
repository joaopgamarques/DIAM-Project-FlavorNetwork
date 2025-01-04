from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import UserRegistrationForm, RecipeSubmissionForm, ChallengeForm
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile, Cookbook, Favorite, RecipeChallenge, Challenge, Rating
from .forms import RecipeForm
from .models import Recipe, User
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.http import HttpResponseNotAllowed
from django.core.paginator import Paginator
from django.db.models import Avg
from .forms import CommentForm
from .models import Comment
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer


# This function checks if the provided user object has the necessary attributes
# and permissions to be considered a superuser.
def is_superuser(user):
    return user.is_authenticated and user.is_superuser


# The home page view.
@login_required(login_url='network:login')
def index(request):
    # Fetch only recipes that are marked as 'published'.
    published_recipes = Recipe.objects.filter(status='published')

    # Fetch challenges that are currently active based on the current UTC time.
    #challenges = Challenge.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())
    challenges = Challenge.objects.order_by('id')[:10]

    # Renders the index page template.
    return render(request, 'network/index.html', {
        'published_recipes': published_recipes,
        'profile': request.user.profile,
        'challenges': challenges,
    })


# Handles user registration with a custom form that includes additional fields like first and last name.
def register(request):
    if request.method == 'POST':
        # If the form is submitted (POST request) bind the POST data to the UserRegistrationForm.
        form = UserRegistrationForm(request.POST)
        # Check if the form is valid (all required fields are filled and valid).
        if form.is_valid():
            # If valid, create a User object from the form, but don't save to the database yet.
            user = form.save(commit=False)
            # Manually set the first_name from the form's cleaned data.
            user.first_name = form.cleaned_data.get('first_name')
            # Manually set the last_name from the form's cleaned data.
            user.last_name = form.cleaned_data.get('last_name')
            # Save the User object to the database.
            user.save()
            # Authenticate the user using the provided credentials.
            user = authenticate(username=user.username, password=request.POST['password1'])
            # Log the user in (creating a user session).
            login(request, user)

            # Redirect the user to the index page after successful registration.
            return redirect('network:index')
    else:
        # If not a POST request, instantiate a new, blank UserRegistrationForm.
        form = UserRegistrationForm()
    # Render the registration page template with the UserRegistrationForm.
    return render(request,  'network/register.html', {
        'form': form,
    })


# Manages user login using the built-in AuthenticationForm.
def user_login(request):
    # If the request is a POST, attempt to process the form data.
    if request.method == 'POST':
        # Create an instance of the AuthenticationForm with the request data.
        form = AuthenticationForm(request, data=request.POST)
        # Check if the form is valid (username and password correct).
        if form.is_valid():
            # Retrieve the username and password from the form data.
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate the user against the database.
            user = authenticate(username=username, password=password)
            # If the user object is not None, the credentials are valid.
            if user is not None:
                login(request, user)  # Log the user in.
                return HttpResponseRedirect(reverse('network:index'))  # Redirect to the index page.
            else:
                # If credentials are not valid, display an error message.
                messages.error(request, 'Invalid username or password.')
        else:
            # If form is not valid, display an error message.
            messages.error(request, 'Invalid username or password.')
    else:
        # If the request is not POST, display the login form.
        form = AuthenticationForm()
    # Render the login page with the AuthenticationForm.

    return render(request,  'network/login.html', {
        'form': form,
    })


# Logs out the current user and redirects to the home page.
@login_required(login_url='network:login')
def user_logout(request):
    logout(request)  # Log the user out.
    return HttpResponseRedirect(reverse('network:login'))  # Redirect to the index page.


# Displays the profile of the currently logged-in user.
@login_required(login_url='network:login')
def profile(request):
    # The user data is automatically included in the request, no need to fetch from database manually.
    return render(request,  'network/profile.html', {
        'profile': request.user.profile,
    })


# Allows users to edit their profile information.
@login_required(login_url='network:login')
def edit_profile(request):
    # Attempt to retrieve the user's profile or create a new one if it does not exist.
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # If the user does not have a profile, create a new one.
        profile = Profile.objects.create(user=request.user)

    # Check if the form submission is a POST request.
    if request.method == 'POST':
        # Create a form instance populated with the POST data and files, linked to the user's profile.
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        # Validate the form.
        if form.is_valid():
            # Save the valid form data to the database.
            form.save()
            # Display a success message to the user.
            messages.success(request, 'Profile updated successfully!')
            # Redirect the user to the profile page after successful update.
            return redirect('network:profile')
    else:
        # If the request is not POST, display the form with existing profile data.
        form = ProfileForm(instance=profile)

    profile = request.user.profile
    # Render the edit profile page with the profile form.
    return render(request,  'network/edit_profile.html', {
        'form': form,
        'profile': profile,
    })


# Enables the user to add a new recipe to the system.
@login_required(login_url='network:login')
def add_recipe(request):
    # Try to retrieve an existing cookbook for the user or create a new one if it does not exist.
    try:
        cookbook = Cookbook.objects.get(user=request.user, title="Cookbook")
    except Cookbook.DoesNotExist:
        # If no cookbook exists for the user, create a new one with a title "Cookbook".
        cookbook = Cookbook.objects.create(user=request.user, title="Cookbook")

    # Check if the form has been submitted (i.e., the request is a POST request).
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding data).
        form = RecipeForm(request.POST, request.FILES)
        # Check if the form is valid (all required fields are filled and valid).
        if form.is_valid():
            # Save the recipe form to create a new Recipe object but don't commit to the database yet.
            recipe = form.save(commit=False)
            # Assign the current user as the creator of the recipe.
            recipe.user = request.user
            # Save the Recipe object to the database.
            recipe.save()
            # Add the newly created recipe to the user's cookbook.
            cookbook.recipes.add(recipe)
            # Redirect to the cookbook of the user after successful recipe creation.
            return redirect('network:view-cookbook', user_id=request.user.id)
    else:
        # If the request is not a POST request, initialize a blank form.
        form = RecipeForm()

    profile = request.user.profile
    # Render the add_recipe.html template with the recipe form.
    return render(request,  'network/add_recipe.html', {
        'form': form,
        'profile': request.user.profile,
    })


# This view function retrieves and displays details of a specific recipe.
@login_required(login_url='network:login')
def view_recipe(request, recipe_id):
    # Retrieve the Recipe object or show a 404 if not found.
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # Check if the current recipe is a favorite of the logged-in user.
    is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe).exists()

    # Aggregate and calculate the average rating for the recipe.
    average_rating_result = Rating.objects.filter(recipe=recipe).aggregate(Avg('score'))
    average_rating = average_rating_result['score__avg'] or 0

    # Retrieve the current user's rating for this recipe, if it exists.
    user_rating = Rating.objects.filter(user=request.user, recipe=recipe_id).first()

    # Retrieve all comments related to this recipe, ordered by their publication date (newest first).
    comments = Comment.objects.filter(recipe=recipe).order_by('-publication_date')

    # Initialize the comment form with POST data, if present.
    comment_form = CommentForm(request.POST or None, auto_id=False)

    # Handle form submission
    if request.method == 'POST' and comment_form.is_valid():
        # Create a new Comment object from the form, but don't save to database yet.
        comment = comment_form.save(commit=False)
        comment.recipe = recipe
        comment.user = request.user
        comment.save()  # Save the comment to the database.
        return redirect('network:view-recipe', recipe_id=recipe_id)  # Redirect to refresh the page.

    # Render the recipe detail page with context data.
    return render(request, 'network/view_recipe.html', {
        'recipe': recipe,
        'is_favorite': is_favorite,
        'rating': user_rating,
        'average_rating': round(average_rating, 1),
        'comments': comments,
        'comment_form': comment_form,
        'profile': request.user.profile,
    })


# Allows logged-in users to view their own cookbook.
@login_required(login_url='network:login')
def view_cookbook(request, user_id):
    # Check if the logged-in user is trying to access their own cookbook.
    if request.user.id != user_id:
        # If not, redirect them to the main index page to prevent unauthorized access.
        return redirect('network:index')

    # Retrieve the Cookbook object associated with the user; 404 if not found.
    cookbook = get_object_or_404(Cookbook, user_id=user_id)

    # Render and return the cookbook page with the cookbook data.
    return render(request,  'network/view_cookbook.html', {
        'cookbook': cookbook,
        'profile': request.user.profile,
    })


# Enables users to edit their recipes.
@login_required(login_url='network:login')
def edit_recipe(request, recipe_id):
    # Fetch the recipe object, ensuring it belongs to the current user. This prevents unauthorized edits.
    recipe = get_object_or_404(Recipe, pk=recipe_id, user=request.user)

    # Check if the form was submitted (POST request).
    if request.method == 'POST':
        # Create a form instance populated with the POST data and associated with the recipe instance.
        form = RecipeForm(request.POST, request.FILES, instance=recipe)

        # Validate the form data.
        if form.is_valid():
            # Save the updated recipe back to the database.
            form.save()
            # Display a success message to the user.
            messages.success(request, 'Recipe updated successfully!')
            # Redirect to the recipe detail view using the recipe's ID.
            return redirect('network:view-recipe', recipe_id=recipe.id)
    else:
        # If the request is not POST, instantiate the form with the recipe instance for initial data.
        form = RecipeForm(instance=recipe)

    # Render the edit_recipe.html template with the form and recipe context.
    return render(request, 'network/edit_recipe.html', {
        'form': form,
        'recipe': recipe,
        'profile': request.user.profile,
    })


# Allows users to add a recipe to their list of favorites.
@login_required(login_url='network:login')
def add_to_favorites(request, recipe_id):
    # Retrieve the Recipe instance by ID or return 404 if not found.
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # Attempt to create a new Favorite object; if it already exists, `created` will be False.
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)

    # If a new Favorite was created, inform the user with a success message.
    if created:
        messages.success(request, "Recipe added to your favorites!")
    # Otherwise, inform the user that the recipe is already in their favorites.
    else:
        messages.info(request, "This recipe is already in your favorites.")

    # Redirect the user back to the recipe's detail view. Ensure that the URL name matches your URL configuration.
    return redirect('network:view-recipe', recipe_id=recipe_id)


# Displays a list of the user's favorite recipes.
@login_required(login_url='network:login')
def view_favorites(request):
    # Retrieve all favorite recipes for the logged-in user.
    user_favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'network/view_favorites.html', {
        'favorites': user_favorites,
        'profile': request.user.profile,
    })


# Handles the removal of a recipe from a user's favorite recipes.
@login_required(login_url='network:login')
def remove_from_favorites(request, recipe_id):
    # Retrieve the Recipe object to ensure it exists; raise 404 if not found.
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # Check if the recipe is already favorited by the user to prevent errors.
    favorite_exists = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
    if favorite_exists:
        # If the favorite exists, delete it and send a success message.
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        messages.success(request, "Recipe removed from your favorites.")
    else:
        # If the favorite does not exist, send an informative message.
        messages.info(request, "Recipe was not in your favorites.")
    return redirect('network:view-recipe', recipe_id=recipe_id)

# This view handles the deletion of a recipe. It ensures that the deletion can only be performed by the user
# who created the recipe or by an admin.
@login_required(login_url='network:login')
def delete_recipe(request, recipe_id):
    # Retrieve the recipe using only the primary key.
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # Check if the logged-in user is the owner of the recipe or if they are a superuser.
    if request.user == recipe.user or request.user.is_superuser:
        # Perform the delete operation.
        recipe.delete()
        # Notify the user of the success.
        messages.success(request, "Recipe deleted successfully.")
        # Redirect to the index page after deletion.
        return redirect('network:index')
    else:
        # If not the owner or a superuser, do not allow deletion.
        messages.error(request, "You do not have permission to delete this recipe.")
        return redirect('network:view-recipe', recipe_id=recipe_id)


# This view displays the feed page to logged-in users.
@login_required(login_url='network:login')
def feed(request):
    # Fetch only recipes that are marked as 'published'.
    published_recipes = Recipe.objects.filter(status='published').order_by('publication_date')
    # Create a paginator object to paginate recipes, showing only 1 recipe per page.
    paginator = Paginator(published_recipes, 1)
    # Get the page number from the request GET parameters.
    page_number = request.GET.get('page')
    # Get the actual page object for the current page number.
    page_obj = paginator.get_page(page_number)

    comments = Comment.objects.filter(recipe=page_obj.object_list[0]).order_by('-publication_date')

    # split ingredients into a list of ingredients
    ingredients_list = [ingredient.strip() for ingredient in page_obj.object_list[0].ingredients.split(';') if ingredient]

    recipe_owner = page_obj.object_list[0].user_id

    # Render the feed template, passing in the page object and the user's profile.
    return render(request, 'network/feed.html', {
        'page_obj': page_obj,
        'profile': request.user.profile,
        'comments': comments,
        'ingredients_list': ingredients_list,
        'recipe_owner': recipe_owner,
    })


# This view allows superusers to add new challenges to the platform.
@user_passes_test(is_superuser, login_url='network:login')
def add_challenge(request):
    # Handle the form submission.
    if request.method == 'POST':
        # Create a form instance with the submitted data.
        form = ChallengeForm(request.POST, request.FILES)
        # Validate the form.
        if form.is_valid():
            # Save the new Challenge to the database.
            form.save()
            # Display a success message to the user.
            messages.success(request, 'Challenge created successfully!')
            # Redirect to the index page after successful creation.
            return redirect('network:index')
    else:
        # If it's not a POST request, create an empty form instance for the user to fill.
        form = ChallengeForm()
    # Render the add_challenge.html template with the form context.
    return render(request, 'network/add_challenge.html', {'form': form,
                                                          'profile': request.user.profile})


# This view displays the details of a specific challenge.
# It also provides authenticated users with a form to submit their recipes to the challenge.
@login_required(login_url='network:login')
def view_challenge(request, challenge_id):
    # Retrieve the Challenge object with the given ID or return a 404 not found error if it doesn't exist.
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    # Fetch the recipes created by the current user.
    user_recipes = Recipe.objects.filter(user=request.user)

    # Handle the form submission.
    if request.method == 'POST':
        # Create a form instance with the submitted data and the current user.
        form = RecipeSubmissionForm(request.POST, user=request.user)
        # Validate the form.
        if form.is_valid():
            # Extract the recipe from the form's cleaned data.
            recipe = form.cleaned_data['recipe']

            # Check if the recipe has already been submitted to the challenge.
            if RecipeChallenge.objects.filter(recipe=recipe, challenge=challenge).exists():
                # If the recipe is already submitted, display an error message.
                messages.error(request, 'This recipe has already been submitted to the challenge.')
            else:
                # If not, create a new RecipeChallenge relationship but don't commit to the database yet.
                recipe_challenge = form.save(commit=False)
                # Set the challenge to the one retrieved based on the challenge_id.
                recipe_challenge.challenge = challenge
                # Save the RecipeChallenge relationship to the database.
                recipe_challenge.save()
                # Display a success message.
                messages.success(request, 'Recipe submitted successfully!')
                # Redirect back to the challenge detail view.
                return redirect('network:view-challenge', challenge_id=challenge.id)
    else:
        # If it's not a POST request, create a form instance with the current user.
        form = RecipeSubmissionForm(user=request.user)
        # Prepopulate the challenge field with the current challenge.
        form.fields['challenge'].initial = challenge
        # Restrict the challenge field to only allow the current challenge.
        form.fields['challenge'].queryset = Challenge.objects.filter(pk=challenge_id)

    # Render the view_challenge.html template with the challenge and form context.
    return render(request, 'network/view_challenge.html', {
        'challenge': challenge,
        'form': form,
        'user_recipes': user_recipes,
        'profile': request.user.profile,
    })


# This view is accessible only by superusers and is used for managing challenges.
@user_passes_test(is_superuser, login_url='network:login')
def manage_challenges(request):
    # Retrieve all challenge objects from the database.
    challenges = Challenge.objects.all()

    # Check if the request method is POST, which means the form has been submitted.
    if request.method == 'POST':
        # Retrieve 'challenge_id' and 'action' from the POST data
        challenge_id = request.POST.get('challenge_id')
        action = request.POST.get('action')

        # If the action specified is 'edit', redirect to the edit page for the specified challenge.
        if action == 'edit':
            return redirect('network:edit-challenge', challenge_id=challenge_id)
        # If the action specified is 'delete', retrieve the challenge object and delete it.
        elif action == 'delete':
            challenge = get_object_or_404(Challenge, pk=challenge_id)
            challenge.delete()
            # Display a success message to the user.
            messages.success(request, "Challenge deleted successfully.")
            # Redirect to the manage challenges page to see the updated list.
            return redirect('network:manage-challenges')

    # Render the manage challenges page with the list of challenges.
    return render(request, 'network/manage_challenges.html', {'challenges': challenges,
                                                              'profile': request.user.profile})


# This view is responsible for deleting a challenge.
@user_passes_test(is_superuser, login_url='network:login')
def delete_challenge(request):
    # Ensure that this view only responds to a POST request.
    if request.method == 'POST':
        # Get the challenge ID from the POST data.
        challenge_id = request.POST.get('challenge_id')
        # Retrieve the challenge instance to be deleted or return a 404 error if not found.
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        # Delete the challenge from the database.
        challenge.delete()
        # Inform the user of the successful deletion.
        messages.success(request, "Challenge deleted successfully.")
        # Redirect back to the challenge management page.
        return redirect('network:manage-challenges')
    else:
        # If the request method is not POST, return an HTTP 405 Method Not Allowed response.
        return HttpResponseNotAllowed(['POST'])


# This view is responsible for editing a challenge.
@user_passes_test(is_superuser, login_url='network:login')
def edit_challenge(request, challenge_id):
    # Retrieve the Challenge object from the database or show a 404 error if not found
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # If the method is POST, it means the form has been submitted.
    if request.method == 'POST':
        # Create a form instance with POST data and files, pre-filled with the challenge instance
        form = ChallengeForm(request.POST, request.FILES, instance=challenge)

        # Check if the form data is valid.
        if form.is_valid():
            # Save the updated challenge to the database.
            form.save()
            # Display a success message to the user.
            messages.success(request, 'Challenge updated successfully!')
            # Redirect to the view page of the updated challenge.
            return redirect('network:view-challenge', challenge_id=challenge.id)
    else:
        # If not a POST method, display the form to edit the challenge.
        form = ChallengeForm(instance=challenge)

    # Render the edit challenge page with the form and challenge data.
    return render(request, 'network/edit_challenge.html', {'form': form, 'challenge': challenge,
                                                           'profile': request.user.profile})


# Handles the deletion of users.
@user_passes_test(is_superuser, login_url='network:login')
def delete_user(request):
    # This view only allows POST requests to ensure that user deletion cannot be triggered accidentally.
    if request.method == 'POST':
        user_id = request.POST.get('user_id')  # Retrieves the user ID from the POST data.
        # Prevents a superuser from deleting their own account, which could lock them out.
        if request.user.id == int(user_id):
            messages.error(request, "You cannot delete yourself.")
            return redirect('network:manage-users')
        # Fetches the user from the database; raises Http404 if not found.
        user_to_delete = get_object_or_404(User, pk=user_id)
        user_to_delete.delete()  # Deletes the user from the database.
        messages.success(request, "User deleted successfully.")
        return redirect('network:manage-users')  # Redirects to the manage users page after deletion.
    else:
        # If a non-POST request is made, returns a 405 Method Not Allowed response.
        return HttpResponseNotAllowed(['POST'])


# Provides a management interface for user accounts.
@user_passes_test(is_superuser, login_url='network:login')
def manage_users(request):
    # Retrieves all users from the database except the currently logged-in superuser to prevent self-deletion.
    users = User.objects.exclude(id=request.user.id)
    # Renders the manage users page, passing the list of users to the template.
    return render(request, 'network/manage_users.html', {
        'users': users,
        'profile': request.user.profile,
    })


# This view handles the rating of a recipe by a logged-in user.
@login_required(login_url='network:login')
def rate_recipe(request, recipe_id):
    # Ensure this view only handles POST requests to secure the action of rating.
    if request.method == 'POST':
        # Check if a Rating already exists for this user and recipe.
        if Rating.objects.filter(user=request.user, recipe=recipe_id).exists():
            # Retrieve the existing Rating object or return a 404 error if not found.
            rating = get_object_or_404(Rating, user_id=request.user, recipe_id=recipe_id)
            # Extract the element ID and the new rating value from the POST data.
            recipe_id = request.POST.get('recipe_id')
            score = request.POST.get('score')
            # Update the score of the rating object.
            rating.score = score
            # Save the updated rating object.
            rating.save()
            # Redirect to the recipe detail view using the recipe's ID.
            return redirect('network:view-recipe', recipe_id=recipe_id)
        else:
            # If the rating does not exist, get the element ID and value from POST data to create a new rating.
            recipe_id = request.POST.get('recipe_id')
            score = request.POST.get('score')
            # Create a new Rating object and save it.
            rating = Rating(recipe_id=recipe_id, score=score, user=request.user)
            rating.save()
            # Redirect to the recipe detail view.
            return redirect('network:view-recipe', recipe_id=recipe_id)
    else:
        # If the request is not a POST, return an HTTP 405 error indicating method not allowed.
        return HttpResponseNotAllowed(['POST'])


# Handles the removal of a recipe from a given challenge.
@login_required(login_url='network:login')
def remove_recipe_from_challenge(request, challenge_id, recipe_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # Ensure the logged-in user is the one who submitted the recipe or a superuser
    if request.user == recipe.user or request.user.is_superuser:
        # Find the RecipeChallenge instance and delete it
        recipe_challenge = get_object_or_404(RecipeChallenge, challenge=challenge, recipe=recipe)
        recipe_challenge.delete()
        messages.success(request, "Recipe removed from the challenge successfully.")
    else:
        messages.error(request, "You do not have permission to remove this recipe.")

    return redirect('network:view-challenge', challenge_id=challenge_id)


# View to create a new message
@api_view(['POST'])
def create_message(request):
    # Handle POST request to create a new message.
    # Create a serializer instance with request data.
    serializer = MessageSerializer(data=request.data)
    # Validate data.
    if serializer.is_valid():
        # Save new message to database.
        serializer.save()
        # Return the newly created message data and HTTP status code 201.
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Return validation errors and HTTP status code 400 if data is invalid.
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to list all users
class UserListView(generics.ListAPIView):
    # API view to retrieve a list of all users.
    # Queryset that defines the collection of data to operate on.
    queryset = User.objects.all()
    # Serializer class to handle queryset serialization.
    serializer_class = UserSerializer


# Retrieve all messages for a specific user, both sent and received.
@api_view(['GET'])
def get_user_messages(request):
    # Retrieve user ID from request query parameters.
    user_id = request.query_params.get('user_id')
    # Get messages where the user is either the sender or the receiver.
    messages = Message.objects.filter(sender_id=user_id) | Message.objects.filter(receiver_id=user_id)
    # Serialize the list of messages.
    serializer = MessageSerializer(messages, many=True)
    # Return the serialized messages.
    return Response(serializer.data)


#  Retrieve details of a specific user by their primary key.
@api_view(['GET'])
def get_user_detail(request, pk):
    try:
        # Attempt to get the user object by primary key.
        user = User.objects.get(pk=pk)
        # Serialize the user data.
        serializer = UserSerializer(user)
        # Return the serialized user data.
        return Response(serializer.data)
    except User.DoesNotExist:
        # Return an error response if the user does not exist.
        return Response({'error': 'User not found'}, status=404)
