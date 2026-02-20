from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from accounts.models import Profile
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class LoginTests(TestCase):

    def setUp(self):
        # Utilisateur client
        self.client_user = User.objects.create_user(username='client1', password='Testpass123')
        Profile.objects.create(user=self.client_user, role='client')

        # Utilisateur pro
        self.pro_user = User.objects.create_user(username='pro1', password='Testpass123')
        Profile.objects.create(user=self.pro_user, role='pro')

        self.login_url = reverse('login')

    # Login client redirection client_dashboard
    def test_login_client_redirect(self):
        response = self.client.post(self.login_url, {
            'username': 'client1',
            'password': 'Testpass123'
        }, follow=True)

        self.assertRedirects(response, reverse('client_dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'client1')

    # Login pro redirection pro_dashboard
    def test_login_pro_redirect(self):
        response = self.client.post(self.login_url, {
            'username': 'pro1',
            'password': 'Testpass123'
        }, follow=True)

        self.assertRedirects(response, reverse('pro_dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'pro1')

    # Login échoué message erreur
    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'client1',
            'password': 'WrongPassword'
        })

        # render 200
        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Nom d'utilisateur ou mot de passe incorrect" in str(m) for m in messages))

    # si rofil manquant il y a message erreur et redirection login
    def test_login_missing_profile(self):
        user_no_profile = User.objects.create_user(username='noprof', password='Testpass123')
        response = self.client.post(self.login_url, {
            'username': 'noprof',
            'password': 'Testpass123'
        }, follow=True)

        # Page rendue
        self.assertEqual(response.status_code, 200)

        # Vérifie le message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Profil utilisateur manquant" in str(m) for m in messages))

    # si utilisateur déjà connecté redirection automatique
    def test_redirect_if_already_logged_in_client(self):
        self.client.login(username='client1', password='Testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('client_dashboard'))

    def test_redirect_if_already_logged_in_pro(self):
        self.client.login(username='pro1', password='Testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('pro_dashboard'))

    # Vérifie que le mot de passe est bien hashé
    def test_password_is_hashed(self):
        user = User.objects.get(username='client1')
        self.assertNotEqual(user.password, 'Testpass123')
        self.assertTrue(user.check_password('Testpass123'))


class PasswordResetTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='client1',
            email='client1@test.com',
            password='Testpass123'
        )

    def test_password_reset_email_sent(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'client1@test.com'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_unknown_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'unknown@test.com'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })

        # GET doit rediriger vers set-password
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("set-password", response.url)

        # Suit la redirection pour poster le nouveau mot de passe
        response = self.client.post(response.url, {
            'new_password1': 'NewStrongPass123',
            'new_password2': 'NewStrongPass123'
        })

        # La POST finale redirige vers password_reset_complete
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset_complete'))

        # Vérifie que le mot de passe a bien été mis à jour
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass123'))

    def test_password_reset_confirm_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.get(
            reverse('password_reset_confirm', kwargs={
                'uidb64': uid,
                'token': 'invalid-token'
            })
        )

        self.assertIn(response.status_code, [200, 302])