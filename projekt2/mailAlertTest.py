from app import create_app, check_price_alerts
from models import db, User, Stock

def run_manual_alert_test(target_email):
    app = create_app()
    
    with app.app_context():
        
        User.query.filter_by(email=target_email).delete()
        db.session.commit()

        
        user = User(username='test_operator', email=target_email, password='123')
        db.session.add(user)
        db.session.commit()
        
        
        stock = Stock(symbol='AAPL', alert_price=1000.0, user_id=user.id)
        db.session.add(stock)
        db.session.commit()
        
        print(f"Inicjacja wysyłki na: {target_email}...")
        
        try:
            
            app.config['TESTING'] = False
            check_price_alerts(app)
            
            # Weryfikacja
            db.session.refresh(stock)
            if stock.alert_price is None:
                print("Sukces: Mail wysłany, alert wyczyszczony w bazie.")
            else:
                print("Błąd: Alert nadal widnieje w bazie.")
                
        except Exception as e:
            print(f"Awaria systemu: {e}")

if __name__ == "__main__":
    email = input("Podaj email do testu: ")
    run_manual_alert_test(email)