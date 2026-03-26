from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Event, UserProfile
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Event, Option, Bet
from django.core.exceptions import ValidationError
import google.generativeai as genai
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import traceback

with open("api.txt", "r", encoding="utf-8") as file:
    api_key = file.read().strip()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def index(request):
    active_events = Event.objects.filter(is_active=True).order_by('end_date')
    context = {'events': active_events}
    return render(request, 'bets/index.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    
    return render(request, 'bets/register.html', {'form': form})

@login_required(login_url='login')
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        option_id = request.POST.get('option')
        amount_str = request.POST.get('amount')
        
        if option_id and amount_str:
            try:
                amount = Decimal(amount_str)
                option = get_object_or_404(Option, id=option_id)
                profile = request.user.profile
                
                if profile.balance < amount:
                    messages.error(request, f"Błąd: Masz za mało środków ({profile.balance} euro).")
                    return redirect('event_detail', event_id=event.id)

                new_bet = Bet(user=request.user, option=option, amount=amount)

                new_bet.full_clean()
                new_bet.save() 

                profile.balance -= amount
                profile.save()
                
                messages.success(request, f"Sukces! Obstawiono {amount} euro.")
                return redirect('dashboard')

            except ValidationError as e:
                messages.error(request, f"Błąd walidacji: {e.message_dict}")
            except Exception as e:
                messages.error(request, f"Błąd: {str(e)}")
        else:
            messages.error(request, "Wypełnij wszystkie pola!")

    return render(request, 'bets/event_detail.html', {'event': event})

@login_required(login_url='login')
def dashboard(request):
    # fix do RelatedObjectDoesNotExist
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if created:
        profile.balance = Decimal('1000.00')
        profile.save()
    
    user_bets = request.user.bets.select_related('option__event').order_by('-created_at')

    if request.method == 'POST' and 'amount' in request.POST:
        try:
            amount_to_add = Decimal(request.POST.get('amount'))
            if amount_to_add > 0:
                profile.balance += amount_to_add
                profile.save()
                messages.success(request, f"Konto zostało doładowane o {amount_to_add} euro!")
            else:
                messages.error(request, "Kwota doładowania musi być większa niż 0.")
        except (ValueError, TypeError):
            messages.error(request, "Wprowadź poprawną kwotę.")
        return redirect('dashboard')

    return render(request, 'bets/dashboard.html', {
        'profile': profile,
        'user_bets': user_bets
    })

@login_required(login_url='login')
def cancel_bet(request, bet_id):
    bet = get_object_or_404(Bet, id=bet_id, user=request.user)
    
    if request.method == 'POST':
        if bet.option.event.is_active:
            profile = request.user.profile
            profile.balance += bet.amount
            profile.save()
            
            bet.delete()
            messages.success(request, f"Anulowano zakład. Zwrócono {bet.amount} euro na Twoje konto.")
        else:
            messages.error(request, "Nie możesz anulować tego zakładu, wydarzenie jest już zamknięte.")
            
    return redirect('dashboard')

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            
            prompt = f"Jesteś asystentem giełdy Prediction Market. Twoje zadanie to udzielanie porad lub pomoc w analizie ryzyka użytkownikom. Nie używaj złożonych dekoratorów ponieważ twoje wiadomości wyświetlają się w prostym chacie. Udzielaj konkretnych, merytorycznych i krótkich odpowiedzi. Oto wiadomość użytkownika: {user_message}"
            response = model.generate_content(prompt)
            
            return JsonResponse({'response': response.text})

        except Exception as e:
            print(traceback.format_exc()) 

            return JsonResponse({'response': f"Asystent AI chwilowo niedostępny, spróbuj ponownie później."})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)