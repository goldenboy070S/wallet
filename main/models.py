from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, time, date
from decimal import Decimal
from django.core.exceptions import ValidationError
# Create your models here.

class User(AbstractUser):
    age = models.IntegerField(default=18, null=True, blank=True)
    phone_number = models.CharField(max_length=150, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class Debtor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField()
    totalDebt = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}"
    

class Debt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.PROTECT)
    amount = models.IntegerField()
    debt_type = models.CharField(max_length=150,choices=(("Given", "GIVEN"), ("Taken", "TAKEN")))
    dueDate = models.DateField()
    status = models.CharField(max_length=150, choices=(("Active", "ACTIVE"), ("Paid", "PAID")))
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.debtor.user.username} - {self.amount} {self.debt_type} due date: {self.dueDate}"
    
    @property
    def total_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def remaining_balance(self):
        """
        Qolgan qarzni hisoblaydi: boshlang'ich qarz miqdori - jami to'langan summa
        """
        return max(self.amount - self.total_paid, 0)  # Qarzni to'lanmagan qismini hisoblash
    
    @property
    def is_paid(self):
        return self.remaining_balance == Decimal("0.00")

    def update_status(self):
        if self.is_paid:
            self.status = 'Pain'  # PAID
        else:
            self.status = 'Active'  # ACTIVE
        self.save()

    
    def extend_due_date_with_interest(self, days, interest_rate=Decimal("0.005")):
        """
        Agar to'lov muddati o'tgan bo'lsa:
        - Muddatni `days` kunga uzaytiradi.
        - Qolgan qarzga `interest_rate` foiz qo'shadi.
        """
        today = date.today()
        
        if today > self.dueDate and not self.is_paid:
            interest = self.remaining_balance * interest_rate
            self.amount += interest.quantize(Decimal("0.01"))
            self.dueDate += timedelta(days=days)
            self.save()

            return f"Muddati {days} kunga uzaytirildi va foiz: {interest} qo'shildi."
        
        return "Muddat tugamagan yoki qarz to'liq to'langan."



class Payment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Payment of {self.amount} for debt {self.debt}"
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    message = models.TextField()  
    is_read = models.BooleanField(default=False, db_index=True)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}..."
