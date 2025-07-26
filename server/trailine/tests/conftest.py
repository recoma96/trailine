import factory

from trailine.apps.privacy_terms.models import PrivacyTerm, PrivacyTermVersion


class PrivacyTermFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PrivacyTerm

    code = factory.Faker("name")


class PrivacyTermVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PrivacyTermVersion

    privacy_term = factory.SubFactory(PrivacyTermFactory)
    version  = 1
    title = factory.Faker("name")
    content = factory.Faker("text")
    is_required = True
