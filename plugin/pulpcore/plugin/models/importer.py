from pulpcore.app.models import Importer as PlatformImporter

from pulpcore.plugin.download.asyncio import DownloaderFactory
from pulpcore.plugin.download.futures import Factory as FuturesFactory


class Importer(PlatformImporter):
    """
    The base importer object to sync content.

    This is meant to be subclassed by plugin authors as an opportunity to provide:

    * Plugin specific sync functionality
    * Add persistent data attributes for a plugin importer subclass

    The sync implementation is provided by :meth: `Importer.sync` which provides more details.
    Failing to implement this method will prevent sync functionality for this plugin type.

    This object is a Django model that inherits from :class: `pulpcore.app.models.Importer` which
    provides the platform persistent attributes for an importer object. Plugin authors can add
    additional persistent importer data by subclassing this object and adding Django fields. We
    defer to the Django docs on extending this model definition with additional fields.

    Validation of the importer is done at the API level by a plugin defined subclass of
    :class: `pulpcore.plugin.serializers.repository.ImporterSerializer`.
    """

    def sync(self, new_version, old_version):
        """
        Perform a sync.

        It is expected that plugins wanting to support sync will provide an implementation on the
        subclassed Importer.

        The model attributes encapsulate all of the information required to sync. This includes the
        platform :class: `pulpcore.app.models.Importer` base attributes and any custom attributes
        defined by the subclass.

        Instantiation and calling of the sync method by the platform is defined by
        :meth: `pulpcore.app.tasks.importer.sync`.

        Subclasses are designed to override this default implementation and should not call super().

        Args:
            new_version (pulpcore.plugin.models.RepositoryVersion): the new version to which content
                should be added and removed.
            old_version (pulpcore.plugin.models.RepositoryVersion): the latest pre-existing version
                or None if one does not exist.
        """
        raise NotImplementedError()

    class Meta:
        abstract = True

    def get_futures_downloader(self, url, destination, artifact=None):
        """
        Get an appropriate download object based on the URL that is fully configured using
        the importer attributes.  When an artifact is specified, the download is tailored
        for the artifact.  Plugin writers are expected to override when additional
        configuration is needed or when another class of download is required.

        Args:

            url (str): The download URL.
            destination (str): The absolute path to where the downloaded file is to be stored.
            artifact (pulpcore.app.models.Artifact): An optional artifact.

        Returns:
            pulpcore.download.futures.Download: The appropriate download object.

        Notes:
            This method supports plugins downloading metadata and the
            `streamer` downloading artifacts.
        """
        return FuturesFactory(self).build(url, destination, artifact)

    @property
    def asyncio_download_factory(self):
        """
        Return the DownloaderFactory which can be used to generate asyncio capable downloaders.

        Upon first access, the DownloaderFactory is instantiated and saved internally.

        Plugin writers are expected to override when additional configuration of the
        DownloaderFactory is needed.

        Returns:
            DownloadFactory: The instantiated DownloaderFactory to be used by
                get_asyncio_downloader()
        """
        try:
            return self._download_factory
        except AttributeError:
            self._download_factory = DownloaderFactory(self)
            return self._download_factory

    def get_asyncio_downloader(self, url, **kwargs):
        """
        Get an asyncio capable downloader that is configured with the importer settings.

        Plugin writers are expected to override when additional configuration is needed or when
        another class of download is required.

        Args:
            url (str): The download URL.
            kwargs (dict): This accepts the parameters of
                :class:`~pulpcore.plugin.download.asyncio.BaseDownloader`.

        Returns:
            subclass of :class:`~pulpcore.plugin.download.asyncio.BaseDownloader`: A downloader that
            is configured with the importer settings.
        """
        return self.asyncio_download_factory.build(url, **kwargs)
