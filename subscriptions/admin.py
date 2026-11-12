from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_cents", "currency", "billing_period", "duration_days", "is_active")
    list_filter = ("is_active", "billing_period")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "started_at", "expires_at", "is_active_display")
    list_filter = ("status", "plan")
    search_fields = ("user__email", "plan__name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    raw_id_fields = ("user",)

    @admin.display(description="Active?", boolean=True)
    def is_active_display(self, obj):
        return obj.is_active
