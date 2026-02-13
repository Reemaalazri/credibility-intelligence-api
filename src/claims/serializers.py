from rest_framework import serializers
from .models import Claim, UserReport


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = "__all__"


class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
