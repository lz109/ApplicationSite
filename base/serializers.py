# myapp/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Candidate, CollegeApplication, Message_new

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    # extra write‑only fields for password confirmation
    password1 = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        # username/email are in Django's default user;
        # role must exist on the user model *or* you will handle it separately.
        fields = ("username", "email", "role", "password1", "password2")

    # ------------------------------------------------------------------
    # 1) cross‑field validation
    # ------------------------------------------------------------------
    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        # Run Django’s built‑in validators (min length, common PW, etc.)
        validate_password(attrs["password1"])
        return attrs

    # ------------------------------------------------------------------
    # 2) create() turns the validated data into a DB row
    # ------------------------------------------------------------------
    def create(self, validated):
        validated.pop("password2")               # not stored
        password = validated.pop("password1")

        # create_user handles username uniqueness + password hashing
        user = User.objects.create_user(**validated)
        user.set_password(password)
        user.save()
        return user



class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

from rest_framework import serializers
from .models import Candidate, Event, User

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class OfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "description", "date", "created_by", "members"]

class CollegeApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeApplication
        fields = ["id", "college_name", "application_status"]

class CandidateListSerializer(serializers.ModelSerializer):
    applications = CollegeApplicationSerializer(source="applications.all", many=True)
    score = serializers.FloatField()

    class Meta:
        model = Candidate
        fields = ["id", "name", "email", "program_fit", "gpa", "score", "applications"]
    
class MessageSerializer(serializers.ModelSerializer):
    sender = OfficerSerializer(read_only=True)
    recipient = OfficerSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='recipient',
        write_only=True
    )

    class Meta:
        model = Message_new
        fields = [
            'id',
            'sender',
            'recipient',
            'recipient_id',
            'subject',
            'body',
            'sent_at',
            'read_at',
            'is_read'
        ]
        read_only_fields = ['id', 'sender', 'sent_at', 'read_at', 'is_read']

    def create(self, validated_data):
        # Automatically set the sender to the current user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)