from celery.app.registry import TaskRegistry
from apps.friendship.contrib.suggestions.backends import importers
from apps.friendship.contrib.suggestions.backends.runners import AsyncRunner
from apps.friendship.contrib.suggestions.settings import RUNNER

if issubclass(RUNNER, AsyncRunner):
    tasks = TaskRegistry()
    tasks.register(importers.GoogleImporter)
    tasks.register(importers.FacebookImporter)
    tasks.register(importers.TwitterImporter)
    tasks.register(importers.YahooImporter)
    tasks.register(importers.LinkedInImporter)

