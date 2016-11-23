from celery import shared_task

from pulp.app import models
from pulp.tasking.tasks import UserFacingTask


@shared_task(base=UserFacingTask)
def delete_publisher(repo_name, publisher_name):
    models.Publisher.objects.filter(name=publisher_name, repository__name=repo_name).delete()


@shared_task(base=UserFacingTask)
def delete_importer(repo_name, importer_name):
    """
    Delete an importer.

    :param repo_name:       the name of a repository
    :type  repo_name:       str
    :param importer_name:   the name of an importer
    :type  importer_name:   str
    """
    models.Importer.objects.filter(name=importer_name, repository__name=repo_name).delete()
