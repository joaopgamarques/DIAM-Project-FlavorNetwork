from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message


# Serializer for Django's User model.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


# Serializer for the Message model.
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sender_details = UserSerializer(source='sender', read_only=True)
    receiver_details = UserSerializer(source='receiver', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'sender_details', 'receiver_details']

    #  Custom validation method to ensure that the sender and receiver are not the same.
    def validate(self, data):
        if data['sender'] == data['receiver']:
            raise serializers.ValidationError("A user cannot send a message to themselves.")
        return data
