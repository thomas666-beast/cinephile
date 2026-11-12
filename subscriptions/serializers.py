from rest_framework import serializers
from .models import SubscriptionPlan, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            "id", "name", "slug", "description", "price_cents",
            "currency", "billing_period", "duration_days",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id", "plan", "status", "started_at", "expires_at",
            "canceled_at", "created_at",
        )


class CreateSubscriptionSerializer(serializers.Serializer):
    """Input serializer for POST /subscriptions/ — client supplies only the plan."""
    plan_slug = serializers.SlugField()
