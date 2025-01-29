from django.db import transaction
from .models import Payment
from decimal import Decimal

def process_payment(debt, amount):
    # amount qiymatini Decimal turiga o'zgartirish
    if isinstance(amount, float):
        amount = Decimal(str(amount))  # float dan decimal ga o'zgartirish
    elif isinstance(amount, int):
        amount = Decimal(amount)  # integer dan decimal ga o'zgartirish

    if amount <= 0:
        raise ValueError("To'lov miqdori 0 dan katta bo'lishi kerak.")
    if debt.amount <= 0:
        raise ValueError("Qarz allaqachon yopilgan.")

    # Qolgan summani tekshirish: Agar to'langan summa qarz miqdoridan ko'proq bo'lsa,
    # faqat qarzni to'lash kerak
    remaining_balance = Decimal(debt.remaining_balance)

    if amount > remaining_balance:
        raise ValueError(f"To'langan summa {remaining_balance} dan oshib ketmoqda.")

    with transaction.atomic():
        # To'lovni saqlash
        Payment.objects.create(
            debt=debt,
            amount=amount,
        )

        # Qarzni yangilash
        debt.save()  # Debt modelidagi amount o'zgarmaydi, faqat to'lovlar kamayadi

    return remaining_balance - amount  # Qolgan summa qaytadi

