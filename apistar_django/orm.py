import typing

from apistar import Component
import django
from django.apps import apps
from django.conf import settings as django_settings
from django.db.models import Model


class Session(object):
    def __init__(self, orm_models: typing.Dict[str, Model]) -> None:
        for name, model in orm_models.items():
            setattr(self, name, model)


class DjangoSessionComponent(Component):
    def __init__(self, settings: typing.Dict=None) -> None:
        django_settings.configure(**settings)
        django.setup()

        self.models = {
            model.__name__: model
            for model in apps.get_models()
        }

    def resolve(self) -> Session:
        return Session(self.models)
