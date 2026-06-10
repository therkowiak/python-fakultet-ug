from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import yfinance as yf
from models import db, Stock
import os 
import google.generativeai as genai

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')
    
    user_stocks = Stock.query.filter_by(user_id=current_user.id).all()
    stock_data = []
    
    for stock in user_stocks:
        
        ticker = yf.Ticker(stock.symbol)
        try:
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError("Brak danych z API")
                
            current_price = hist['Close'].iloc[-1]
            stock_data.append({
                'id': stock.id,
                'symbol': stock.symbol,
                'price': round(current_price, 2),
                'alert_price': stock.alert_price
            })
        except Exception:
            stock_data.append({
                'id': stock.id,
                'symbol': stock.symbol,
                'price': 'Błąd',
                'alert_price': stock.alert_price
            })
            
    return render_template('dashboard.html', stocks=stock_data)

@main_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    stock_info = None
    symbol = None
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        
        ticker = yf.Ticker(symbol)
        try:
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError("Brak danych z API")
                
            current_price = hist['Close'].iloc[-1]
            stock_info = {
                'symbol': symbol,
                'price': round(current_price, 2)
            }
        except Exception:
            flash(f'Nie znaleziono danych dla symbolu {symbol}. Upewnij się, że jest poprawny.', 'danger')
    
    return render_template('search.html', stock_info=stock_info, symbol=symbol)

@main_bp.route('/add_stock', methods=['POST'])
@login_required
def add_stock():
    symbol = request.form.get('symbol')
    alert_price = request.form.get('alert_price')
    
    if not symbol:
        flash('Brak symbolu.', 'danger')
        return redirect(url_for('main.search'))
        
    existing_stock = Stock.query.filter_by(user_id=current_user.id, symbol=symbol).first()
    if existing_stock:
        flash(f'Już obserwujesz akcje {symbol}.', 'warning')
    else:
        new_stock = Stock(
            symbol=symbol, 
            alert_price=float(alert_price) if alert_price else None,
            user_id=current_user.id
        )
        db.session.add(new_stock)
        db.session.commit()
        flash(f'Dodano {symbol} do obserwowanych!', 'success')
        
    return redirect(url_for('main.index'))

@main_bp.route('/delete_stock/<int:stock_id>', methods=['POST'])
@login_required
def delete_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    if stock.user_id == current_user.id:
        db.session.delete(stock)
        db.session.commit()
        flash(f'Usunięto {stock.symbol} z obserwowanych.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        
        if new_username and new_email:
            current_user.username = new_username
            current_user.email = new_email
            db.session.commit()
            flash('ZAKTUALIZOWANO_DANE_PRAWIDŁOWO.', 'success')
        else:
            flash('BŁĄD: POLA_NIE_MOGĄ_BYĆ_PUSTE.', 'danger')
            
    return render_template('profile.html')

#Projekt 4 - Dodanie GEMINI AI

#Odczyt klucza API z pliku
API_KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'api_key.txt')

try:
    with open(API_KEY_PATH, 'r') as file:
        api_key = file.read().strip()
        genai.configure(api_key=api_key)
        print("SYS_MSG: Pomyślnie załadowano klucz API z api_key.txt")
except FileNotFoundError:
    print(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku z kluczem API w lokalizacji: {API_KEY_PATH}")

model = genai.GenerativeModel('gemini-2.5-flash')

@main_bp.route('/ask_gemini', methods=['POST'])
@login_required
def ask_gemini():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'Brak komunikatu'}), 400

    # Prompt systemowy który "wczuwa" model w rolę
    prompt = f"""
    Jesteś analitykiem giełdowym AI w systemie monitorowania cen akcji i wysylania alertów 'Binturong Signals'. 
    Twój ton to profesjonalny operator terminala.
    Odpowiadaj konkretnie, ale wyczerpująco. Jeśli użytkownik pyta o konkretną spółkę, zrób krótkie podsumowanie jej obecnej sytuacji rynkowej, trendów lub głośnych newsów z nią związanych. Używaj formatowania (wypunktowania), aby odpowiedź była czytelna.
    
    ZAPYTANIE UŻYTKOWNIKA: {user_message}
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': f'Błąd API: {str(e)}'}), 500