from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User

from .helpers import assign_wallet_on_registration
from .models import Profile, Wallet, CustomUser


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()
#
#
# @receiver(post_save, sender=User)
# def update_profile(sender, instance, created, **kwargs):
#     if not created:
#         instance.profile.save()
#         print('Profile updated')
# # post_save.connect(update_profile, sender=User)


@receiver(user_logged_in)
def user_login_handler(sender, request, user, **kwargs):
    # Perform actions here before redirecting to LOGIN_REDIRECT_URL
    print('user_login_handler')
    print(user.id)
    try:
        wallet = Wallet.objects.get(user_id=user.id)
    except Wallet.DoesNotExist:
        wallet = None

    print('wallet')
    print(wallet)
    if wallet is None:
        # Assign a UserWallet if not already assigned
        print('Assign a UserWallet if not already assigned')
        print('profile')
        print(user.assigned_profile)
        assign_wallet_on_registration(request, user, user.assigned_profile)

pass