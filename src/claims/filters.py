import django_filters
from .models import Claim


class ClaimFilter(django_filters.FilterSet):
    speaker_exact = django_filters.CharFilter(field_name="speaker", lookup_expr="iexact")
    speaker_contains = django_filters.CharFilter(field_name="speaker", lookup_expr="icontains")

    statement_contains = django_filters.CharFilter(field_name="statement", lookup_expr="icontains")

    class Meta:
        model = Claim
        fields = ["label", "party", "state", "split"]