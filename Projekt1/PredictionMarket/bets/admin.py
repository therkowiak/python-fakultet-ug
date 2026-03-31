from django.contrib import admin
from .models import UserProfile, Category, Event, Option, Bet, Message

# Konfiguracja Event - dodanie pola winning_option
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'end_date', 'winning_option')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'description')
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('title', 'category', 'description')
        }),
        ('Status i daty', {
            'fields': ('is_active', 'created_at', 'end_date')
        }),
        ('Rozliczenie', {
            'fields': ('winning_option',),
            'description': 'Ustaw wygraną opcję aby rozliczyć wszystkie zakłady na to wydarzenie'
        }),
    )
    readonly_fields = ('created_at',)

# Konfiguracja Bet - wyświetlanie statusu rozliczenia
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'option', 'amount', 'created_at', 'is_resolved', 'is_won')
    list_filter = ('is_resolved', 'is_won', 'created_at')
    search_fields = ('user__username', 'option__name')
    readonly_fields = ('created_at',)

# Konfiguracja Message - wyświetlanie komunikatów
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'message_type', 'amount', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'content')
    readonly_fields = ('created_at', 'user', 'bet')
    fieldsets = (
        ('Informacje o wiadomości', {
            'fields': ('user', 'message_type', 'title', 'created_at')
        }),
        ('Zawartość', {
            'fields': ('content', 'amount')
        }),
        ('Powiązanie', {
            'fields': ('bet', 'is_read')
        }),
    )

# rejestracja modeli
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Event, EventAdmin)
admin.site.register(Option)
admin.site.register(Bet, BetAdmin)
admin.site.register(Message, MessageAdmin)