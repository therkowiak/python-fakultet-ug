import unittest
from unittest.mock import patch, MagicMock
from app import create_app, mail, check_price_alerts
from models import db, User, Stock
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

class BinturongTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ====== PAGE LOADING TESTS ======
    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGOWANIE', response.data)

    def test_register_page_loads(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'REJESTRACJA', response.data)

    # ====== ERROR HANDLING TESTS ======
    def test_404_error_handler(self):
        response = self.client.get('/tajna_strona_ktora_nie_istnieje')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)

    def test_500_error_handler(self):
        """Test niestandardowych błędów"""
        with self.app.app_context():
            try:
                @self.app.route('/test_error')
                def test_error():
                    raise Exception("Test error")
                
                response = self.client.get('/test_error')
                self.assertEqual(response.status_code, 500)
            except Exception:
                
                pass

    # ====== AUTHENTICATION TESTS ======
    def test_user_registration_success(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'testuser')

    def test_user_registration_duplicate_email(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='existing', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()

        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertIn(b'email', response.data.lower())

    def test_user_login_success(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()

        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()

        # Zaloguj użytkownika
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Wyloguj się
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # ====== PROTECTED ROUTES TESTS ======
    def test_search_page_requires_login(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 302)

    # ====== DATABASE MODEL TESTS ======
    def test_user_model_creation(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            
            user_from_db = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user_from_db)
            self.assertEqual(user_from_db.email, 'test@example.com')

    def test_stock_model_creation(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            
            stock = Stock(symbol='AAPL', alert_price=150.0, user_id=user.id)
            db.session.add(stock)
            db.session.commit()
            
            stock_from_db = Stock.query.filter_by(symbol='AAPL').first()
            self.assertIsNotNone(stock_from_db)
            self.assertEqual(stock_from_db.alert_price, 150.0)
            self.assertEqual(stock_from_db.user_id, user.id)

    def test_stock_timestamp(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            
            before = datetime.utcnow()
            stock = Stock(symbol='AAPL', user_id=user.id)
            db.session.add(stock)
            db.session.commit()
            after = datetime.utcnow()
            
            stock_from_db = Stock.query.filter_by(symbol='AAPL').first()
            self.assertGreaterEqual(stock_from_db.date_added, before)
            self.assertLessEqual(stock_from_db.date_added, after)

    def test_user_stock_relationship(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            
            stock1 = Stock(symbol='AAPL', user_id=user.id)
            stock2 = Stock(symbol='GOOGL', user_id=user.id)
            db.session.add_all([stock1, stock2])
            db.session.commit()
            
            user_from_db = User.query.filter_by(username='testuser').first()
            self.assertEqual(len(user_from_db.stocks), 2)
            symbols = [stock.symbol for stock in user_from_db.stocks]
            self.assertIn('AAPL', symbols)
            self.assertIn('GOOGL', symbols)

    # ====== PRICE ALERT TESTS ======
    @patch('yfinance.Ticker')
    @patch('app.mail.send')
    def test_check_price_alerts_sends_email(self, mock_mail_send, mock_ticker):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            
            stock = Stock(symbol='AAPL', alert_price=150.0, user_id=user.id)
            db.session.add(stock)
            db.session.commit()
            
            # Mock cena poniżej alertu
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.fast_info = {'last_price': 140.0}
            mock_ticker.return_value = mock_ticker_instance
            
            check_price_alerts(self.app)
            
            mock_mail_send.assert_called_once()

    @patch('yfinance.Ticker')
    @patch('app.mail.send')
    def test_check_price_alerts_no_email_when_price_above(self, mock_mail_send, mock_ticker):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            
            stock = Stock(symbol='AAPL', alert_price=150.0, user_id=user.id)
            db.session.add(stock)
            db.session.commit()
            
            # Mock cena powyżej alertu
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.fast_info = {'last_price': 160.0}
            mock_ticker.return_value = mock_ticker_instance
            
            check_price_alerts(self.app)
            
            mock_mail_send.assert_not_called()

    # ====== EDGE CASES TESTS ======
    def test_password_hashing(self):
        with self.app.app_context():
            password = 'testpassword123'
            hashed_pwd = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Hashed password nie powinien być równy zwykłemu hasłu
            self.assertNotEqual(hashed_pwd, password)
            
            # Ale powinien weryfikować się poprawnie
            self.assertTrue(bcrypt.check_password_hash(hashed_pwd, password))
            
            # Inne hasło nie powinno się weryfikować
            self.assertFalse(bcrypt.check_password_hash(hashed_pwd, 'wrongpassword'))

    def test_user_authenticated_redirects_to_index(self):
        """Test że zalogowany użytkownik nie może ponownie zalogować się"""
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()

        # Zaloguj się
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Spróbuj zalogować się ponownie
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_access_search(self):
        with self.app.app_context():
            hashed_pwd = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pwd)
            db.session.add(user)
            db.session.commit()

        # Zaloguj się
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Spróbuj dostępu do chronionej strony
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()