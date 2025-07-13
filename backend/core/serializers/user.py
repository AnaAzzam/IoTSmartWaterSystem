
from rest_framework import serializers
from core.models.base import CustomUser, WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert, WaterConsumptionThreshold
from django.contrib.auth.password_validation import validate_password

# Existing serializers (unchanged)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'role', 'home_address', 'phone_number', 'email', 'created_at']

class WaterConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterConsumption
        fields = '__all__'

class TankFlowMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankFlowMetric
        fields = '__all__'

class LeakageDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakageDetection
        fields = '__all__'

class WaterConsumptionAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterConsumptionAlert
        fields = '__all__'

class WaterConsumptionThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterConsumptionThreshold
        fields = '__all__'

class HistoricalDataFilterSerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=['minute', 'daily', 'weekly', 'monthly'], required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    metric_type = serializers.ChoiceField(choices=['tank_level', 'main_flow_rate', 'secondary_flow_rate'], required=False)
    detection_type = serializers.ChoiceField(choices=['first_pir', 'second_pir', 'leak_alarm'], required=False)

# Updated serializers for bulk control
class CommandSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[
            'home/tankRoom/motor',
            'home/tankRoom/tankValve',
            'home/tankRoom/mainValve',
            'home/tankRoom/cadoValve',
            'home/tankRoom/automode'
        ],
        required=True
    )
    value = serializers.BooleanField(required=True)

class BulkControlSerializer(serializers.Serializer):
    commands = serializers.ListField(child=CommandSerializer(), required=True, min_length=1)

# Existing serializers (unchanged)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(required=True)
    home_address = serializers.CharField(required=False, allow_blank=True)

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required for registration.")
        return value

    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number', 'email', 'full_name', 'home_address', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        if CustomUser.objects.filter(phone_number=attrs['phone_number']).exists():
            raise serializers.ValidationError({"phone_number": "Phone number already exists."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            home_address=validated_data.get('home_address', ''),
            password=validated_data['password'],
            role='homeowner'
        )
        return user

class LoginSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_phone = attrs.get('username_or_phone')
        password = attrs.get('password')

        user = None
        if username_or_phone:
            try:
                user = CustomUser.objects.get(username=username_or_phone)
            except CustomUser.DoesNotExist:
                try:
                    user = CustomUser.objects.get(phone_number=username_or_phone)
                except CustomUser.DoesNotExist:
                    pass

        if user and user.check_password(password):
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError("Invalid credentials")
















# from rest_framework import serializers
# from core.models.base import CustomUser, WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert, WaterConsumptionThreshold
# from django.contrib.auth.password_validation import validate_password

# # Existing serializers (unchanged)
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'full_name', 'role', 'home_address', 'phone_number', 'email', 'created_at']

# class WaterConsumptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WaterConsumption
#         fields = '__all__'

# class TankFlowMetricSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TankFlowMetric
#         fields = '__all__'

# class LeakageDetectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeakageDetection
#         fields = '__all__'

# class WaterConsumptionAlertSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WaterConsumptionAlert
#         fields = '__all__'

# class WaterConsumptionThresholdSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WaterConsumptionThreshold
#         fields = '__all__'

# class HistoricalDataFilterSerializer(serializers.Serializer):
#     period = serializers.ChoiceField(choices=['minute', 'daily', 'weekly', 'monthly'], required=False)
#     start_date = serializers.DateTimeField(required=False)
#     end_date = serializers.DateTimeField(required=False)
#     metric_type = serializers.ChoiceField(choices=['tank_level', 'main_flow_rate', 'secondary_flow_rate'], required=False)
#     detection_type = serializers.ChoiceField(choices=['first_pir', 'second_pir', 'leak_alarm'], required=False)

# # Updated serializers for bulk control
# class CommandSerializer(serializers.Serializer):
#     topic = serializers.CharField(max_length=255, required=True)
#     value = serializers.BooleanField(required=True)

# class BulkControlSerializer(serializers.Serializer):
#     commands = serializers.ListField(child=CommandSerializer(), required=True)

# # Existing serializers (unchanged)
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)
#     phone_number = serializers.CharField(required=True)
#     email = serializers.EmailField(required=True)
#     full_name = serializers.CharField(required=True)
#     home_address = serializers.CharField(required=False, allow_blank=True)

#     def validate_phone_number(self, value):
#         if not value:
#             raise serializers.ValidationError("Phone number is required for registration.")
#         return value

#     class Meta:
#         model = CustomUser
#         fields = ('username', 'phone_number', 'email', 'full_name', 'home_address', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password2": "Password fields didn't match."})
#         if CustomUser.objects.filter(email=attrs['email']).exists():
#             raise serializers.ValidationError({"email": "Email already exists."})
#         if CustomUser.objects.filter(phone_number=attrs['phone_number']).exists():
#             raise serializers.ValidationError({"phone_number": "Phone number already exists."})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         user = CustomUser.objects.create_user(
#             username=validated_data['username'],
#             phone_number=validated_data['phone_number'],
#             email=validated_data['email'],
#             full_name=validated_data['full_name'],
#             home_address=validated_data.get('home_address', ''),
#             password=validated_data['password'],
#             role='homeowner'
#         )
#         return user

# class LoginSerializer(serializers.Serializer):
#     username_or_phone = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         username_or_phone = attrs.get('username_or_phone')
#         password = attrs.get('password')

#         user = None
#         if username_or_phone:
#             try:
#                 user = CustomUser.objects.get(username=username_or_phone)
#             except CustomUser.DoesNotExist:
#                 try:
#                     user = CustomUser.objects.get(phone_number=username_or_phone)
#                 except CustomUser.DoesNotExist:
#                     pass

#         if user and user.check_password(password):
#             attrs['user'] = user
#             return attrs
#         raise serializers.ValidationError("Invalid credentials")










# # from rest_framework import serializers
# # from core.models.base import CustomUser, WaterConsumption, TankFlowMetric, LeakageDetection, WaterConsumptionAlert, WaterConsumptionThreshold
# # from django.contrib.auth.password_validation import validate_password

# # # Existing serializers (keep these unchanged)
# # class UserSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = CustomUser
# #         fields = ['id', 'username', 'full_name', 'role', 'home_address', 'phone_number', 'email', 'created_at']

# # class WaterConsumptionSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = WaterConsumption
# #         fields = '__all__'

# # class TankFlowMetricSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = TankFlowMetric
# #         fields = '__all__'

# # class LeakageDetectionSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = LeakageDetection
# #         fields = '__all__'

# # class WaterConsumptionAlertSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = WaterConsumptionAlert
# #         fields = '__all__'

# # class WaterConsumptionThresholdSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = WaterConsumptionThreshold
# #         fields = '__all__'


# # class HistoricalDataFilterSerializer(serializers.Serializer):
# #     period = serializers.ChoiceField(choices=['minute', 'daily', 'weekly', 'monthly'], required=False)
# #     start_date = serializers.DateTimeField(required=False)
# #     end_date = serializers.DateTimeField(required=False)
# #     metric_type = serializers.ChoiceField(choices=['tank_level', 'main_flow_rate', 'secondary_flow_rate'], required=False)
# #     detection_type = serializers.ChoiceField(choices=['first_pir', 'second_pir', 'leak_alarm'], required=False)

# # # class BulkControlSerializer(serializers.Serializer):
# # #     commands = [
# # #         {
# # #             'topic': serializers.CharField(),
# # #             'value': serializers.BooleanField(),
# # #         }
# # #     ]


# # class CommandSerializer(serializers.Serializer):
# #     topic = serializers.CharField(max_length=255, required=True)
# #     value = serializers.BooleanField(required=True)

# # class BulkControlSerializer(serializers.Serializer):
# #     commands = serializers.ListField(child=CommandSerializer(), required=True)


# # # Add new serializers
# # class RegisterSerializer(serializers.ModelSerializer):
# #     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
# #     password2 = serializers.CharField(write_only=True, required=True)
# #     phone_number = serializers.CharField(required=True)
# #     email = serializers.EmailField(required=True)
# #     full_name = serializers.CharField(required=True)
# #     home_address = serializers.CharField(required=False, allow_blank=True)


# #     # Validate phone number to ensure it is provided 27/6
# #     def validate_phone_number(self, value):
# #          if not value:
# #             raise serializers.ValidationError("Phone number is required for registration.")
# #          return value
# #     class Meta:
# #         model = CustomUser
# #         fields = ('username', 'phone_number', 'email', 'full_name', 'home_address', 'password', 'password2')

# #     def validate(self, attrs):
# #         if attrs['password'] != attrs['password2']:
# #             raise serializers.ValidationError({"password2": "Password fields didn't match."})
# #         if CustomUser.objects.filter(email=attrs['email']).exists():
# #             raise serializers.ValidationError({"email": "Email already exists."})
# #         if CustomUser.objects.filter(phone_number=attrs['phone_number']).exists():
# #             raise serializers.ValidationError({"phone_number": "Phone number already exists."})
# #         return attrs

# #     def create(self, validated_data):
# #         validated_data.pop('password2')
# #         user = CustomUser.objects.create_user(
# #             username=validated_data['username'],
# #             phone_number=validated_data['phone_number'],
# #             email=validated_data['email'],
# #             full_name=validated_data['full_name'],
# #             home_address=validated_data.get('home_address', ''),
# #             password=validated_data['password'],
# #             role='homeowner'
# #         )
# #         return user

# # class LoginSerializer(serializers.Serializer):
# #     username_or_phone = serializers.CharField()
# #     password = serializers.CharField(write_only=True)

# #     def validate(self, attrs):
# #         username_or_phone = attrs.get('username_or_phone')
# #         password = attrs.get('password')

# #         user = None
# #         if username_or_phone:
# #             try:
# #                 user = CustomUser.objects.get(username=username_or_phone)
# #             except CustomUser.DoesNotExist:
# #                 try:
# #                     user = CustomUser.objects.get(phone_number=username_or_phone)
# #                 except CustomUser.DoesNotExist:
# #                     pass

# #         if user and user.check_password(password):
# #             attrs['user'] = user
# #             return attrs
# #         raise serializers.ValidationError("Invalid credentials")