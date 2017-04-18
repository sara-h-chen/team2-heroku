from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from models import Food, Message, Preference
from django.contrib.auth.models import User


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class PreferenceSerializer(serializers.ModelSerializer):
    preference_user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Preference
        fields = ('preference_user', 'preference')


class FoodListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Food
        fields = ('id', 'food_name', 'quantity', 'date_listed', 'food_type', 'allergens',
                  'status', 'latitude', 'longitude', 'picture', 'user')


# UNUSED SERIALIZER
class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(format=None, input_formats=None)
    sender = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ('sender', 'receiver', 'msg_content', 'created_at', 'read', 'id')


