from django.core.management.base import BaseCommand
from django.utils import timezone
from bets.models import Event, Bet, Message
from decimal import Decimal

class Command(BaseCommand):
    help = 'Zamyka wydarzenia, których czas dobiegł końca i rozlicza wszystkie zakłady'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event-id',
            type=int,
            help='ID konkretnego wydarzenia do zamknięcia (opcjonalne)',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Jeśli podano konkretne event-id, zakm zamknij tylko to
        if options.get('event_id'):
            expired_events = Event.objects.filter(
                id=options['event_id'],
                is_active=True,
                end_date__lte=now
            )
        else:
            # W przeciwnym razie - aktywne wydarzenia, których data końca minęła
            expired_events = Event.objects.filter(
                is_active=True,
                end_date__lte=now
            )
        
        count = 0
        for event in expired_events:
            # Sprawdź czy już rozliczono
            if event.winning_option is None:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Wydarzenie '{event.title}' nie ma wyznaczonej opcji wygranej. Pomiń.")
                )
                continue
            
            # Rozlicz wszystkie zakłady na to wydarzenie
            self.settle_bets_for_event(event)
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ SUKCES: Rozliczono i zamknięto {count} wydarzeń.')
        )

    def settle_bets_for_event(self, event):
        """Rozlicza wszystkie zakłady dla danego wydarzenia"""
        
        self.stdout.write(f"\n📋 Rozliczanie wydarzenia: {event.title}")
        self.stdout.write(f"  Wygrana opcja: {event.winning_option.name}")
        
        # Pobierz wszystkie nierozliczone zakłady na to wydarzenie
        unresolved_bets = Bet.objects.filter(
            option__event=event,
            is_resolved=False
        ).select_related('user', 'option')
        
        total_bets = unresolved_bets.count()
        winning_bets = unresolved_bets.filter(option=event.winning_option)
        losing_bets = unresolved_bets.exclude(option=event.winning_option)
        
        self.stdout.write(f"  Razem zakładów: {total_bets}")
        self.stdout.write(f"  Wygranych: {winning_bets.count()}")
        self.stdout.write(f"  Przegranych: {losing_bets.count()}")
        
        # Rozlicz wygranych
        for bet in winning_bets:
            self.process_winning_bet(bet)
        
        # Rozlicz przegranych
        for bet in losing_bets:
            self.process_losing_bet(bet)
        
        # Zamknij wydarzenie
        event.is_active = False
        event.save()
        
        self.stdout.write(self.style.SUCCESS(f"  ✓ Wydarzenie zamknięte"))

    def process_winning_bet(self, bet):
        """Przetwarza wygrany zakład - zwraca stawkę + wygrane"""
        
        winnings = bet.amount * Decimal(str(bet.option.odds))
        total_payout = bet.amount + winnings  # stawka + wygrane
        
        # Zaktualizuj saldo użytkownika
        user_profile = bet.user.profile
        user_profile.balance += total_payout
        user_profile.save()
        
        # Oznacz zakład jako rozliczony
        bet.is_resolved = True
        bet.is_won = True
        bet.save()
        
        # Wyślij wiadomość o wygranej
        message_content = (
            f"🎉 Gratulacje! Twój zakład na '{bet.option.name}' wygrał!\n\n"
            f"📊 Szczegóły:\n"
            f"  • Postawiona kwota: {bet.amount:.2f} €\n"
            f"  • Zysk (po kursie {bet.option.odds}): {winnings:.2f} €\n"
            f"  • Łączna wypłata: {total_payout:.2f} €\n"
            f"  • Twoje nowe saldo: {user_profile.balance:.2f} €"
        )
        
        Message.objects.create(
            user=bet.user,
            bet=bet,
            message_type='win',
            title=f"Wygrana w wydarzeniu '{bet.option.event.title}'",
            content=message_content,
            amount=total_payout
        )
        
        self.stdout.write(
            f"    ✓ @{bet.user.username} - WYGRANA {total_payout:.2f}€ (zysk: {winnings:.2f}€)"
        )

    def process_losing_bet(self, bet):
        """Przetwarza przegrany zakład - brak zwrotu"""
        
        # Oznacz zakład jako rozliczony
        bet.is_resolved = True
        bet.is_won = False
        bet.save()
        
        # Wyślij wiadomość o przegranej
        message_content = (
            f"❌ Niestety, Twój zakład na '{bet.option.name}' przegrał.\n\n"
            f"📊 Szczegóły:\n"
            f"  • Postawiona kwota: {bet.amount:.2f} €\n"
            f"  • Wygrana opcja: '{bet.option.event.winning_option.name}'\n"
            f"  • Strata: {bet.amount:.2f} €\n"
            f"  • Twoje aktualne saldo: {bet.user.profile.balance:.2f} €"
        )
        
        Message.objects.create(
            user=bet.user,
            bet=bet,
            message_type='loss',
            title=f"Przegrana w wydarzeniu '{bet.option.event.title}'",
            content=message_content,
            amount=Decimal('0.00')
        )
        
        self.stdout.write(
            f"    • @{bet.user.username} - PRZEGRANA {bet.amount:.2f}€"
        )