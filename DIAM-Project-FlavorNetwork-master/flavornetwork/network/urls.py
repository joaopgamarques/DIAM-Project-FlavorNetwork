from django.urls import path
from . import views
from .views import UserListView, get_user_detail

# Namespace for your application.
# This allows you to organize URLs by application and use the name when referring to them.
app_name = 'network'

urlpatterns = [
    # Endpoint to retrieve a list of all users.
    path('api/users/', UserListView.as_view(), name='user-list'),
    # Endpoint to create a new message.
    path('api/messages/', views.create_message, name='create-message'),
    # Endpoint to retrieve all messages related to a specific user, either sent or received.
    path('api/messages/by_user/', views.get_user_messages, name='get_user_messages'),
    # Endpoint to retrieve detailed information about a specific user by their ID.
    path('api/users/<int:pk>/', get_user_detail, name='user-detail'),
    # Home page URL. This is the root URL for the application.
    path("", views.index, name="index"),
    # User registration URL. It shows the registration form and processes the user registration.
    path('register/', views.register, name='register'),
    # Login URL. It shows the login form and logs the user in.
    path('login/', views.user_login, name='login'),
    # Logout URL. It logs the user out.
    path('logout/', views.user_logout, name='logout'),
    # User profile URL. It displays the profile of the logged-in user.
    path('profile/', views.profile, name='profile'),
    # Edit profile URL. It shows the form to edit the user's profile and saves the changes.
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    # Add recipe URL. It displays the form to create a new recipe and adds it to the database.
    path('add-recipe/', views.add_recipe, name='add-recipe'),
    # View recipe details URL. It takes a recipe ID and displays the recipe's details.
    path('recipes/<int:recipe_id>/', views.view_recipe, name='view-recipe'),
    # View user cookbook URL. It takes a user ID and displays their cookbook.
    path('cookbook/<int:user_id>/', views.view_cookbook, name='view-cookbook'),
    # Edit recipe URL. It takes a recipe ID, shows the form to edit the recipe, and saves the changes.
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit-recipe'),
    # View favorites URL. It displays a list of the user's favorite recipes.
    path('favorites/', views.view_favorites, name='view-favorites'),
    # Add to favorites URL. It takes a recipe ID and adds the recipe to the user's favorites.
    path('recipe/<int:recipe_id>/add_to_favorites/', views.add_to_favorites, name='add-to-favorites'),
    # Remove from favorites URL. It takes a recipe ID and removes the recipe from the user's favorites.
    path('recipe/<int:recipe_id>/remove_from_favorites/', views.remove_from_favorites, name='remove-from-favorites'),
    # Delete recipe URL. It takes a recipe ID, allows only the creator or an admin to delete it,
    # and then redirects to an appropriate page after deletion.
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete-recipe'),
    # This URL endpoint directs to the 'feed' view which displays the user's feed.
    path('feed/', views.feed, name='feed'),
    # Add challenge URL. Allows superusers to create new cooking challenges.
    path('add-challenge/', views.add_challenge, name='add-challenge'),
    # View challenge details URL. It takes a challenge ID and displays details including its recipes,
    # and allows authenticated users to submit their recipes to the challenge.
    path('challenges/<int:challenge_id>/', views.view_challenge, name='view-challenge'),
    # This URL directs to a view that allows superusers to manage challenges,
    # typically listing them with options to edit or delete.
    path('manage-challenges/', views.manage_challenges, name='manage-challenges'),
    # This URL directs to the edit page for a specific challenge.
    path('challenge/<int:challenge_id>/edit/', views.edit_challenge, name='edit-challenge'),
    # This URL handles the deletion of a challenge based on a POST request.
    # The view will check if the user is a superuser before allowing the challenge to be deleted.
    path('challenge/delete/', views.delete_challenge, name='delete-challenge'),
    # This URL directs to a view that lists all the users, allowing superusers to manage user accounts.
    path('manage-users/', views.manage_users, name='manage-users'),
    # This URL handles the deletion of a user.
    path('delete-user/', views.delete_user, name='delete-user'),
    # This URL handles the rating of a recipe
    path('recipes/<int:recipe_id>/rate/', views.rate_recipe, name='rate-view'),
    # This URL handles the remove of a recipe from a challenge
    path('challenges/<int:challenge_id>/remove-recipe/<int:recipe_id>/', views.remove_recipe_from_challenge, name='remove-recipe-from-challenge'),
]
