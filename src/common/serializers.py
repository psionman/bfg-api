
from rest_framework import serializers
from common.models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["name", "last_task", "last_data", "board"]