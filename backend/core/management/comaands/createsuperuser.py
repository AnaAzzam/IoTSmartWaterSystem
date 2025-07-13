
from django.contrib.auth.management.commands import createsuperuser
from core.forms import CustomUserCreationForm
from core.models import CustomUser
class Command(createsuperuser.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = CustomUser
        self.form = CustomUserCreationForm
