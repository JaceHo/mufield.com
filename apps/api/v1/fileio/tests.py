from django.test import TestCase

from apps.api.models import Music


# Create your tests here.
class MusicTest(TestCase):
    def setUp(self):
        Music.objects.create(name='O\'Reilly')

    def test_can_save(self):
        music = Music(name="O'Reilly")
        music.save()
