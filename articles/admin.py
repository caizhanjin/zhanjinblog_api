from django.contrib import admin

from .models import Articles, Collections, Labels, Messages

admin.site.register(Articles)
admin.site.register(Collections)
admin.site.register(Labels)
admin.site.register(Messages)
