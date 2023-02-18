from rest_framework import serializers
from user_app.models import User, UserOTP, UserPasswordResetToken

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer to be used when registering a user.
    """
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

class UserOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for User model output (to be nested in other serializers).
    """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'user_slug',
            'phone'
        )

class UserOTPSerializer(serializers.ModelSerializer):
    """
    Serializer for UserOTP model.
    """
    class Meta:
        model = UserOTP
        fields = '__all__'


class UserPasswordResetTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPasswordResetToken
        fields = '__all__'