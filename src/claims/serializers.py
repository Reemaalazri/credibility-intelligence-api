from rest_framework import serializers
from .models import Claim, UserReport
from django.contrib.auth.models import User


# Serializer for exposing LIAR dataset claims through the API
class ClaimSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="claim-detail",
        lookup_field="pk"
    )

    class Meta:
        model = Claim
        fields = [
            "url",
            "id",
            "liar_id",
            "label",
            "statement",
            "subjects",
            "speaker",
            "speaker_job_title",
            "state",
            "party",
            "barely_true_count",
            "false_count",
            "half_true_count",
            "mostly_true_count",
            "pants_on_fire_count",
            "context",
            "split",
            "created_at",
        ]


# Serializer for user-submitted reports about potentially misleading claims
class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]

    # Prevent normal users from changing report status (only admins can)
    def validate(self, attrs):
        request = self.context.get("request")

        if request and not request.user.is_staff:
            if self.instance:
                if "status" in attrs:
                    attrs["status"] = self.instance.status
            else:
                attrs.pop("status", None)

        return attrs


# Prevent normal users from changing report status (only admins can)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    # Prevent normal users from changing report status (only admins can)
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


# Serializer describing the links returned by the API root endpoint
class ApiRootSerializer(serializers.Serializer):
    claims = serializers.URLField()
    reports = serializers.URLField()
    score = serializers.URLField()
    register = serializers.URLField()
    login = serializers.URLField()


# Serializer for validating incoming claim text sent to the scoring endpoint
class ScoreRequestSerializer(serializers.Serializer):
    text = serializers.CharField()


# Serializer representing the credibility summary returned by the scoring system
class ScoreSummarySerializer(serializers.Serializer):
    final_verdict = serializers.CharField()
    final_credibility_score = serializers.IntegerField()
    final_risk_score = serializers.IntegerField()
    final_confidence = serializers.IntegerField()


# Serializer describing the full response returned by the scoring API
class ScoreResponseSerializer(serializers.Serializer):
    claim = serializers.CharField()
    summary = ScoreSummarySerializer()
    local_analysis = serializers.JSONField()
    external_analysis = serializers.JSONField()
    fusion = serializers.JSONField()


# Serializer describing the full response returned by the scoring API
class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
