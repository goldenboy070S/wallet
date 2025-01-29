from rest_framework.routers import DefaultRouter
from .views import DebtorViewSet, DebtViewSet, PaymentViewSet, UserViewSet, NotificationViewSet

router = DefaultRouter()
router.register('debtors', DebtorViewSet)
router.register('debts', DebtViewSet)
router.register('users', UserViewSet, basename="user")
router.register('payments', PaymentViewSet, basename="payment")
router.register('notifications', NotificationViewSet, basename='notification')

urlpatterns = router.urls