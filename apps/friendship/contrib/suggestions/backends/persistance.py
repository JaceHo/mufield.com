import warnings

from apps.friendship.contrib.suggestions.models import ImportedContact
warnings.filterwarnings('ignore', message="^Data truncated for column.*$")

class BasePersistance(object):
    def persist(self, contact, status, credentials):
        if status is None:
            status = self.default_status()
        return self.persist_contact(contact, status, credentials)

    def persist_contact(self, contact, status, credentials):
        return status


class ModelPersistance(BasePersistance):

    def persist_contact(self, contact, status, credentials):
        try:
            obj, created = ImportedContact.objects.get_or_create(
                owner=credentials["user"],
                email=contact["email"],
                name=contact["name"],
            )
        except:
            created = False
        status["total"] += 1
        if created:
            status["imported"] += 1
        return status

