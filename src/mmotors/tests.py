from django.test import TestCase


class ErrorPagesTests(TestCase):

    def test_404_page(self):
        response = self.client.get("/page-qui-nexiste-pas/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_403_page(self):
        response = self.client.get("/test403/")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")