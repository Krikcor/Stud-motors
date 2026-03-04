from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from accounts.models import Profile


class RegistrationTests(TestCase):

    def setUp(self):
        self.register_url = reverse('register')

        self.valid_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean@example.com',
            'username': 'jean123',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
        }

    # Test inscription valide
    def test_register_valid_user(self):
        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='jean123').exists())

    # Vérifie que le mot de passe est hashé
    def test_password_is_hashed(self):
        self.client.post(self.register_url, self.valid_data)

        user = User.objects.get(username='jean123')

        self.assertNotEqual(user.password, 'Testpassword123')
        self.assertTrue(user.check_password('Testpassword123'))

    # Vérifie que le Profile est créé avec rôle client
    def test_profile_created_with_client_role(self):
        self.client.post(self.register_url, self.valid_data)

        user = User.objects.get(username='jean123')
        profile = Profile.objects.get(user=user)

        self.assertEqual(profile.role, 'client')

    # Vérifie que l'utilisateur est connecté automatiquement
    def test_user_is_logged_in_after_registration(self):
        response = self.client.post(self.register_url, self.valid_data, follow=True)

        user = User.objects.get(username='jean123')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'], user)

    # Test email déjà utilisé
    def test_register_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='jean@example.com',
            password='Testpassword123'
        )

        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "déjà utilisée")

    # Test mot de passe invalide
    def test_register_invalid_password(self):
        data = self.valid_data.copy()
        data['password1'] = '123'
        data['password2'] = '123'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='jean123').exists())

    # Test message Django succès
    def test_success_message_displayed(self):
        response = self.client.post(self.register_url, self.valid_data, follow=True)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Compte client créé" in str(m) for m in messages))

    # Test redirection si utilisateur déjà connecté
    def test_redirect_if_user_already_logged_in(self):
        user = User.objects.create_user(
            username='loggeduser',
            password='Testpassword123'
        )

        self.client.login(username='loggeduser', password='Testpassword123')
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 302)

    def test_register_duplicate_username_case_insensitive(self):
        User.objects.create_user(
            username='Jean123',
            email='other@example.com',
            password='Testpassword123'
        )

        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 200)

        # Toujours un seul utilisateur
        self.assertEqual(User.objects.filter(username__iexact='jean123').count(), 1)

        self.assertContains(response, "déjà utilisé")

    def test_no_profile_created_if_username_duplicate(self):
        User.objects.create_user(
            username='jean123',
            email='other@example.com',
            password='Testpassword123'
        )

        self.client.post(self.register_url, self.valid_data)

        # Toujours un seul user
        self.assertEqual(User.objects.filter(username='jean123').count(), 1)

        # Toujours un seul profil associé
        self.assertEqual(Profile.objects.count(), 0)


from django.core import mail


class WelcomeEmailTests(TestCase):

    def setUp(self):
        self.register_url = reverse('register')

        self.valid_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean_welcome@example.com',
            'username': 'jean_welcome',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
        }

    # Vérifie qu'un email de bienvenue est envoyé
    def test_welcome_email_sent(self):
        self.client.post(self.register_url, self.valid_data)

        self.assertEqual(len(mail.outbox), 1)

    # Vérifie le sujet de l'email
    def test_welcome_email_subject(self):
        self.client.post(self.register_url, self.valid_data)

        self.assertIn("Bienvenue", mail.outbox[0].subject)

    # Vérifie le destinataire
    def test_welcome_email_recipient(self):
        self.client.post(self.register_url, self.valid_data)

        self.assertEqual(mail.outbox[0].to, ['jean_welcome@example.com'])

    # Vérifie le contenu du message
    def test_welcome_email_content(self):
        self.client.post(self.register_url, self.valid_data)

        self.assertIn("Jean", mail.outbox[0].body)
        self.assertIn("compte a bien été créé", mail.outbox[0].body)