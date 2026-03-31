from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# 1. Model profilu użytkownika
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, validators=[MinValueValidator(0)]) # (na start 1000)

    def __str__(self):
        return f"{self.user.username} - {self.balance} pkt"
    
    def clean(self):
        if self.balance < 0:
            raise ValidationError({'balance': 'Saldo nie może być ujemne.'})
        
    def save(self, *args, **kwargs):
        self.full_clean()                    # uruchamia wszystkie walidacje
        super().save(*args, **kwargs)

# 2. Model kategorii
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# 3. Model wydarzenia
class Event(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    winning_option = models.ForeignKey('Option', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_events')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

# 4. Model opcji zakładu
class Option(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    initial_liquidity = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def __str__(self):
        return f"{self.name} (Kurs: {self.odds}) - {self.event.title}"

    @property
    def option_pool(self):
        # Prawdziwe zakłady graczy + wirtualna płynność z panelu admina
        from django.db.models import Sum
        from decimal import Decimal
        real_bets = self.bets.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return self.initial_liquidity + real_bets

    @property
    def odds(self):
        #Całkowita pula wydarzenia / pula na tę opcję
        event_pool = sum(opt.option_pool for opt in self.event.options.all())
        return round(event_pool / self.option_pool, 2)

    @property
    def percentage(self):
        event_pool = sum(opt.option_pool for opt in self.event.options.all())
        return round((self.option_pool / event_pool) * 100, 1)
    
    @property
    def percentage_int(self):
        return int(self.percentage)
        
# 5. Model konkretnego zakładu postawionego przez użytkownika
class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='bets')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]   # minimalna stawka 0.01
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)

    def __str__(self):
        return f"Zakład {self.user.username} na {self.option.name} za {self.amount}"

    def clean(self):
        if not self.option.event.is_active:
            raise ValidationError({'option': 'Nie można obstawiać nieaktywnego wydarzenia.'})

        if self.option.event.end_date <= timezone.now():
            raise ValidationError({'option': 'Wydarzenie już się zakończyło – nie można obstawiać.'})

        try:
            profile = self.user.profile
            if self.amount > profile.balance:
                raise ValidationError({'amount': f'Nie masz wystarczającego salda. Masz tylko {profile.balance}.'})
        except AttributeError:
            raise ValidationError({'user': 'Użytkownik nie ma profilu.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def calculate_winnings(self):
        """Oblicza wygrane na podstawie kursu i kwoty zakładu"""
        if not self.is_resolved:
            return None
        return self.amount * float(self.option.odds)


# 6. Model komunikatów dla użytkowników
class Message(models.Model):
    MESSAGE_TYPES = [
        ('win', 'Wygrana'),
        ('loss', 'Przegrana'),
        ('info', 'Informacja'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    bet = models.ForeignKey(Bet, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='info')
    title = models.CharField(max_length=200)
    content = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # kwota wygranej/przegrany/info
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_message_type_display()}] {self.title} - {self.user.username}"