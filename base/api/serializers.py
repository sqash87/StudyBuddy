from rest_framework.serializers import ModelSerializer
from base.models import Room

#take the all the fielfds of the Room model and return as the json object.
class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
