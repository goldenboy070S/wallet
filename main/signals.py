from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date, timedelta
from .models import Debt, Notification
from django.core.mail import send_mail
from django.conf import settings  


@receiver(post_save, sender=Debt)
def update_total_debt(sender, instance, **kwargs):
    debtor = instance.debtor  # Debtga tegishli Debtorni olish
    total_debt = debtor.totalDebt  # Joriy totalDebtni olish

    if instance.amount >= total_debt:  # Agar amount totalDebtni to'lay olsa
        debtor.totalDebt = 0  # Barcha qarz yopiladi
        debtor.save()
    elif instance.amount < total_debt:  # Agar amount kam bo'lsa
        debtor.totalDebt -= instance.amount  # TotalDebtni kamaytirish
        debtor.save()


@receiver(post_save, sender=Debt)
def notify_due_date(sender, instance, created, **kwargs):
    if not created:  
        remaining_days = (instance.dueDate - date.today()).days
        if remaining_days <= 3:  
            notification = Notification.objects.create(
                user=instance.debtor.user,  
                message=f"Diqqat! Sizning qarzingiz ({instance.amount}) muddati {instance.dueDate} kuni tugaydi."
            )
            try:
                send_due_date_notification(notification)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")

def send_due_date_notification(notification_instance):
    subject = 'Qarz muddati yaqinlashmoqda!'
    message = f"Salom {notification_instance.user.first_name},\n\n{notification_instance.message}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [notification_instance.user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")