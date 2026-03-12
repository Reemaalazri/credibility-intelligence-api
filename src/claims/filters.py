import django_filters
from .models import Claim


# Filter configuration for querying Claim records from the LIAR dataset
class ClaimFilter(django_filters.FilterSet):
    # Exact match filter for speaker name
    speaker_exact = django_filters.CharFilter(field_name="speaker", lookup_expr="iexact")

    # Partial match filter for speaker name
    speaker_contains = django_filters.CharFilter(field_name="speaker", lookup_expr="icontains")

    # Search within claim statements
    statement_contains = django_filters.CharFilter(field_name="statement", lookup_expr="icontains")

    class Meta:
        model = Claim   # Apply filters to the Claim model
        fields = ["label", "party", "state", "split"]   # Allow filtering by these fields
