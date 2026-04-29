import unittest
from unittest.mock import patch
from app import create_app, mail, check_price_alerts
from models import db, User, Stock

class BinturongTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGOWANIE', response.data)

    def test_404_error_handler(self):
        response = self.client.get('/tajna_strona_ktora_nie_istnieje')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)

    def test_search_page_requires_login(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()