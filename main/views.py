from django.shortcuts import render
from .serializers import DebtSerializer, DebtorSerializer, PaymentSerializer, UserCreateSerializer, NotificationSerializer, UserUpdateSerializer
from.models import Debtor, Debt, Payment, Notification
from rest_framework.viewsets import ModelViewSet
from .models import User
from rest_framework.permissions import BasePermission
from .services import process_payment
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
# Create your views here.

class DebtorViewSet(ModelViewSet):
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class IsAuthenticatedOrPostOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and not request.user.is_authenticated or request.user.is_superuser:
            return True
        elif request.method == 'GET' and request.user.is_superuser:
            return True
        return False    


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrPostOnly]  
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserUpdateSerializer


class DebtViewSet(ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(debtor__user=self.request.user)
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError({"error": e.messages})  # DRF formatiga o'tkazish

    def perform_update(self, serializer):
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError({"error": e.messages})


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        debt_id = data.get('debt')
        amount = data.get('amount')

        if not debt_id or not amount:
            return Response({"error": "Qarz ID va to'lov miqdorini kiriting."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "To'lov miqdori noto'g'ri formatda."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            debt = Debt.objects.get(id=debt_id)
            remaining_amount = process_payment(debt, amount)
            
            return Response({
                "message": "To'lov muvaffaqiyatli amalga oshirildi.",
                "remaining_amount": remaining_amount  # Qolgan summa qaytariladi
            }, status=status.HTTP_201_CREATED)

        except Debt.DoesNotExist:
            return Response({"error": "Bunday qarz mavjud emas."}, status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
        

class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
