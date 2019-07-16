from django.contrib import admin

# Register your models here.

from cereslibrary.models import Tech #,Product

#admin.site.register(Product)
#admin.site.register(Tech)

class TechAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'investment_cost', 'operation_cost', 'benefits')
    list_filter = ('product', 'benefits')
    fieldsets = (
        (None, {
            'fields':('title', 'product')
            }),
        ('Economic parameters', {
            'fields':('investment_cost', 'operation_cost', 'benefits')})
    )

admin.site.register(Tech, TechAdmin)
