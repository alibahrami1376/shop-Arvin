from django.contrib import admin
from website.models import ContactModel
# Register your models here.
@admin.register(ContactModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "phone_number",
        "subject",
        "content",
        "is_seen",
        "created_date",

    )
