from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookstore.models import Book, Category


class SearchViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Science")
        cls.other_category = Category.objects.create(name="History")
        cls.science_book = Book.objects.create(
            category=cls.category,
            isbn="SCI-001",
            title="Modern Physics",
            author="Ada Newton",
            publisher="Academy Press",
            date_published=timezone.now(),
        )
        cls.history_book = Book.objects.create(
            category=cls.other_category,
            isbn="HIS-001",
            title="Ancient Worlds",
            author="Mary Curie",
            publisher="Scholars Press",
            date_published=timezone.now(),
        )

    def test_search_matches_book_title(self):
        response = self.client.get(reverse("search:search"), {"q": "physics"})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book"].object_list,
            [self.science_book],
        )

    def test_search_matches_category_name(self):
        response = self.client.get(reverse("search:search"), {"q": "science"})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book"].object_list,
            [self.science_book],
        )

    def test_search_matches_author_text_field(self):
        response = self.client.get(reverse("search:search"), {"q": "curie"})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book"].object_list,
            [self.history_book],
        )
