from rest_framework import serializers
from accounts.profile_models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    initial = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "name", "is_kids", "initial", "created_at")
        read_only_fields = ("id", "initial", "created_at")

    def validate_name(self, value):
        v = value.strip()
        if not v:
            raise serializers.ValidationError("Name cannot be blank.")
        if len(v) > 50:
            raise serializers.ValidationError("Name must be ≤ 50 characters.")
        return v

    def validate(self, attrs):
        user = self.context["request"].user
        name = attrs.get("name")
        if name:
            qs = Profile.objects.filter(user=user, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"name": "You already have a profile with this name."}
                )
        if self.instance is None:
            if Profile.objects.filter(user=user).count() >= 5:
                raise serializers.ValidationError(
                    "Maximum of 5 profiles per account."
                )
        return attrs
