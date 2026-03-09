from django.db import models
from django.contrib.auth.models import User

# Create models


class Claim(models.Model):

    # LIAR dataset claim record (TSV columns 1–14) + split.

    class Split(models.TextChoices):
        TRAIN = "train", "Train"
        VALID = "valid", "Validation"
        TEST = "test", "Test"

    class Label(models.TextChoices):
        TRUE = "true", "true"
        MOSTLY_TRUE = "mostly-true", "mostly-true"
        HALF_TRUE = "half-true", "half-true"
        BARELY_TRUE = "barely-true", "barely-true"
        FALSE = "false", "false"
        PANTS_FIRE = "pants-fire", "pants-fire"

    # Column 1: ID of the statement ([ID].json)
    liar_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Dataset statement id (e.g., 12134.json).",
    )

    # Column 2: label
    label = models.CharField(
        max_length=20,
        choices=Label.choices,
        db_index=True,
        help_text="Truthfulness label from LIAR dataset.",
    )

    # Column 3: statement
    statement = models.TextField(help_text="The claim text / statement.")

    # Column 4: subject(s) (comma-separated in the dataset)
    subjects = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Comma-separated subjects/topics.",
    )

    # Column 5: speaker
    speaker = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="Speaker name/id (as in dataset).",
    )

    # Column 6: speaker's job title
    speaker_job_title = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Speaker job title (may be empty).",
    )

    # Column 7: state info
    state = models.CharField(
        max_length=60,
        blank=True,
        default="",
        db_index=True,
        help_text="State information (may be empty).",
    )

    # Column 8: party affiliation
    party = models.CharField(
        max_length=60,
        blank=True,
        default="",
        db_index=True,
        help_text="Party affiliation (may be empty, e.g., republican/democrat/none).",
    )

    # Columns 9–13: credit history counts
    barely_true_count = models.PositiveIntegerField(default=0)
    false_count = models.PositiveIntegerField(default=0)
    half_true_count = models.PositiveIntegerField(default=0)
    mostly_true_count = models.PositiveIntegerField(default=0)
    pants_on_fire_count = models.PositiveIntegerField(default=0)

    # Column 14: context (venue/location)
    context = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Context/venue/location of the statement.",
    )

    # Extra: which file split it came from
    split = models.CharField(
        max_length=10,
        choices=Split.choices,
        db_index=True,
        help_text="Dataset split (train/valid/test).",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.liar_id} [{self.label}]"

    @property
    def total_history(self) -> int:
        """Total credit history counts (cols 9–13)."""
        return (
            self.barely_true_count
            + self.false_count
            + self.half_true_count
            + self.mostly_true_count
            + self.pants_on_fire_count
        )


class UserReport(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        REVIEWED = "reviewed", "Reviewed"
        RESOLVED = "resolved", "Resolved"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        UNKNOWN = "unknown", "Unknown"

    statement_text = models.TextField()
    speaker = models.CharField(max_length=100, blank=True, default="")
    report_reason = models.TextField(blank=True, default="")

    # Filled by scoring logic later (start simple now)
    risk_score = models.FloatField(default=0.0)
    risk_level = models.CharField(
        max_length=10, choices=RiskLevel.choices, default=RiskLevel.UNKNOWN
    )

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OPEN
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Report #{self.id} ({self.status})"
