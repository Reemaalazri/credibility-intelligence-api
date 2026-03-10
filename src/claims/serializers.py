from rest_framework import serializers
from .models import Claim, UserReport
from django.contrib.auth.models import User


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


class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class ApiRootSerializer(serializers.Serializer):
    claims = serializers.URLField()
    reports = serializers.URLField()
    score = serializers.URLField()
    register = serializers.URLField()
    login = serializers.URLField()


class ScoreRequestSerializer(serializers.Serializer):
    text = serializers.CharField()


class ScoreSummarySerializer(serializers.Serializer):
    final_verdict = serializers.CharField()
    final_credibility_score = serializers.IntegerField()
    final_risk_score = serializers.IntegerField()
    final_confidence = serializers.IntegerField()


class ScoreResponseSerializer(serializers.Serializer):
    claim = serializers.CharField()
    summary = ScoreSummarySerializer()
    local_analysis = serializers.JSONField()
    external_analysis = serializers.JSONField()
    fusion = serializers.JSONField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()