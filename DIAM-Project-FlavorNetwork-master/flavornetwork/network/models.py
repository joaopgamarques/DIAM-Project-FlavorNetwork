import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


# Profile Model: This model extends the User model to add additional profile information.
class Profile(models.Model):
    # Creates a one-to-one relationship between User and Profile models.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Stores user's culinary preferences, can be empty.
    culinary_preferences = models.TextField(blank=True)
    # Stores user's dietary restrictions, can be empty.
    dietary_restrictions = models.TextField(blank=True)
    # Stores user's image.
    image = models.ImageField(upload_to='users/images/', default='users/images/default.png', blank=True)

    # Defines the string representation of the model, which in this case, returns the username's profile.
    def __str__(self):
        return f"{self.user.username}'s profile"


# This signal receiver function is connected to the post_save signal of the User model.
# It is triggered every time a User instance is saved.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # If a new User instance is created ('created' is True), then a new Profile instance
    # is also created and associated with this User.
    if created:
        Profile.objects.create(user=instance)
        Cookbook.objects.create(user=instance, title="Cookbook")  # Create a default cookbook.
    # If the User instance is not new (it is being updated), then the associated Profile
    # instance is also saved to catch any changes.
    else:
        instance.profile.save()


# Recipe Model: Represents a cooking recipe with various details.
class Recipe(models.Model):
    # Enumeration of possible statuses for a recipe.
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    # Title of the recipe.
    title = models.CharField(max_length=255)
    # The user who created the recipe, establishing a many-to-one relationship.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    # Detailed description of the recipe including instructions.
    description = models.TextField()
    # List of ingredients required for the recipe.
    ingredients = models.TextField()
    # Steps for preparing the recipe.
    preparation_steps = models.TextField()
    # Time taken to prepare the recipe in minutes.
    preparation_time = models.IntegerField()
    # An image representing the recipe, stored using the specified file system storage.
    images = models.ImageField(upload_to='recipes/images/', blank=True, null=True)
    # Date and time when the recipe was published, automatically set when the recipe is first created.
    publication_date = models.DateTimeField(auto_now_add=True)
    # The current status of the recipe.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    # Additional fields for storing nutritional information of the recipe.
    calories = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fat = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    carbs = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    proteins = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Defines the string representation of the model to return the recipe title.
    def __str__(self):
        return self.title


# Comment Model: Represents comments made by users on recipes.
class Comment(models.Model):
    # The recipe to which the comment belongs.
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    # The user who made the comment.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    # The content of the comment.
    text = models.TextField()
    # The date and time the comment was made, automatically set to the current date and time.
    publication_date = models.DateTimeField(auto_now_add=True)

    # Returns a string that identifies the comment by the username and the recipe title.
    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"


# Rating Model: Represents ratings given by users for recipes.
class Rating(models.Model):
    # The recipe being rated.
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    # The user who gave the rating.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    # The rating score.
    score = models.IntegerField()
    # An optional comment to accompany the rating.
    comment = models.TextField(blank=True)

    # Custom clean method to validate the rating score.
    def clean(self):
        if not (1 <= self.score <= 5):
            raise ValidationError('Score must be between 1 and 5.')

    # Returns a string representation of the rating including the user, score, and recipe.
    def __str__(self):
        return f"Rating {self.score}/5 by {self.user.username} for {self.recipe.title}"


# Challenge Model: Represents cooking challenges that can include multiple recipes.
class Challenge(models.Model):
    # The title of the challenge.
    title = models.CharField(max_length=255)
    # A detailed description of what the challenge entails.
    description = models.TextField()
    # The start date and time of the challenge.
    start_date = models.DateTimeField()
    # The end date and time of the challenge.
    end_date = models.DateTimeField()
    # Many-to-many relationship with recipes. A challenge can have multiple recipes and a recipe can be part of
    # multiple challenges.
    recipes = models.ManyToManyField(Recipe, through='RecipeChallenge', related_name='challenges')
    # An image representing the challenge, stored using the specified file system storage.
    image = models.ImageField(upload_to='challenges/images/', blank=True, null=True)

    # Custom clean method to ensure the challenge end date is after the start date.
    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        if self.start_date < timezone.now():
            raise ValidationError("Start date must be in the future.")

    # String representation of the challenge model.
    def __str__(self):
        return self.title


# RecipeChallenge Model: Intermediate model for the many-to-many relationship between Recipes and Challenges.
class RecipeChallenge(models.Model):
    # The recipe involved in the challenge.
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # The challenge in which the recipe is participating.
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    # The submission date of the recipe to the challenge.
    submission_date = models.DateTimeField(auto_now_add=True)

    # String representation to identify a recipe's participation in a challenge.
    def __str__(self):
        return f"{self.recipe.title} in {self.challenge.title}"


# Favorite Model: Represents a user's saved favorite recipes.
class Favorite(models.Model):
    # The user who has marked the recipe as a favorite.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    # The recipe that has been marked as a favorite.
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    # String representation of a favorite, showing the user and the recipe.
    def __str__(self):
        return f"{self.user.username}'s favorite recipe {self.recipe.title}"


# Cookbook Model: Represents a collection of recipes created by a user.
class Cookbook(models.Model):
    # The owner of the cookbook.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cookbooks')
    # Many-to-many relationship to allow a cookbook to have multiple recipes.
    recipes = models.ManyToManyField(Recipe)
    # The title of the cookbook.
    title = models.CharField(max_length=100)
    # An optional description of the cookbook.
    description = models.TextField(blank=True, null=True)

    # String representation of the cookbook, indicating the title and the owner.
    def __str__(self):
        return f"{self.user.username}'s cookbook: {self.title}"


# Message Model: Represents direct messages sent between users.
class Message(models.Model):
    # The sender of the message.
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # The recipient of the message.
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # The content of the message.
    message = models.TextField()
    # The timestamp of when the message was sent.
    timestamp = models.DateTimeField(auto_now_add=True)

    # String representation showing the sender and receiver of the message.
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
