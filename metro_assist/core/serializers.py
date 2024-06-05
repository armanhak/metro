from rest_framework import serializers
from .models import Passenger, Request, Employee#, WorkSchedule

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

# class WorkScheduleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkSchedule
#         fields = '__all__'