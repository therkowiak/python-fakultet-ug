from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf

from models import db, User, Stock
from routes.auth import auth_bp
from routes.main import main_bp
from dotenv import load_dotenv
import os
load_dotenv()

mail = Mail()

def check_price_alerts(app):
    """Funkcja uruchamiana w tle, która sprawdza ceny i wysyła maile."""
    with app.app_context():
        stocks_with_alerts = Stock.query.filter(Stock.alert_price.isnot(None)).all()
        
        for stock in stocks_with_alerts:
            ticker = yf.Ticker(stock.symbol)
            try:
                current_price = ticker.fast_info['last_price']
                
                if current_price <= stock.alert_price:
                    user = User.query.get(stock.user_id)
                    
                    # Przygotowanie i wysłanie maila
                    msg = Message(
                        subject=f"Binturong Signals: {stock.symbol} osiągnął cel!",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[user.email]
                    )
                    msg.body = f"Witaj {user.username},\n\nCena akcji {stock.symbol} właśnie osiągnęła Twój alert ({stock.alert_price} $).\nAktualna cena to: {round(current_price, 2)} $.\n\nPozdrawiamy,\nZespół Binturong Signals"
                    mail.send(msg)
                
                    stock.alert_price = None
                    db.session.commit()
                    print(f"Wysłano alert dla {stock.symbol} do {user.email}")
            except Exception as e:
                print(f"Błąd sprawdzania ceny dla {stock.symbol}: {e}")

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'domyslny-klucz-awaryjny')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gielda.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Konfiguracja poczty
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    db.init_app(app)
    mail.init_app(app)

    # Konfiguracja logowania
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Rejestracja Blueprintów
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Obsługa błędów 404 i 500
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Inicjalizacja bazy
    with app.app_context():
        db.create_all()

    # Uruchomienie schedulera
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: check_price_alerts(app), trigger="interval", minutes=1)
    scheduler.start()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)