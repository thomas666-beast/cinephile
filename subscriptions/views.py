from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .access import get_active_subscription
from .models import SubscriptionPlan, Subscription
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer, CreateSubscriptionSerializer,
)
from django.http import Http404
from datetime import timedelta


class PlanListAPIView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class CreateSubscriptionAPIView(generics.GenericAPIView):
    serializer_class = CreateSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan_slug = serializer.validated_data["plan_slug"]

        try:
            plan = SubscriptionPlan.objects.get(slug=plan_slug, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Plan not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Reject if already subscribed
        existing = get_active_subscription(request.user)
        if existing:
            return Response(
                {"detail": "You already have an active subscription.",
                 "subscription_id": existing.id},
                status=status.HTTP_409_CONFLICT,
            )

        # Simulated payment: immediately active. Real payment integration later.
        expires_at = timezone.now() + timedelta(days=plan.duration_days)
        with transaction.atomic():
            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                status=Subscription.Status.ACTIVE,
                expires_at=expires_at,
            )

        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED,
        )

class MySubscriptionAPIView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        subscription = get_active_subscription(self.request.user)
        if subscription is None:
            raise Http404("No active subscription.")
        return subscription


class CancelSubscriptionAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        subscription = Subscription.objects.filter(
            pk=pk, user=request.user,
        ).first()
        if not subscription:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if subscription.status != Subscription.Status.ACTIVE:
            return Response(
                {"detail": f"Subscription is {subscription.status}."},
                status=status.HTTP_409_CONFLICT,
            )
        subscription.status = Subscription.Status.CANCELED
        subscription.canceled_at = timezone.now()
        subscription.save(update_fields=["status", "canceled_at"])
        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_200_OK)
