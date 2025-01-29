from rest_framework import serializers
from .models import Debt, Debtor, Payment, Notification
from .models import User

class DebtSerializer(serializers.ModelSerializer):
    payment_info = serializers.SerializerMethodField()

    class Meta:
        model = Debt
        fields = ['id', 'debtor', 'amount', 'debt_type', 'dueDate', 'status', 'payment_info']

    def get_payment_info(self, obj):
        return {
            "total_paid": obj.total_paid,
            "remaining_balance": obj.remaining_balance
        }
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Qarz miqdori 0 dan katta bo‘lishi kerak.")
        return value
    
    def validate(self, data):
        debtor = data.get("debtor")
        amount = data.get("amount")

        if debtor and amount > debtor.totalDebt:
            raise serializers.ValidationError(
                {"amount": f"Amount ({amount}) cannot exceed debtor's total debt ({debtor.totalDebt})."}
            )
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'age', 'email', 'phone_number']

    def validate_age(self, value):
        if value < 17 or value > 100:
            raise serializers.ValidationError("Yosh chegarasi 20 dan 100 gacha bo'lishi kerak.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirmation']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DebtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtor
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
    

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'