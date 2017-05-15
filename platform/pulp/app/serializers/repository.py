from gettext import gettext as _

from rest_framework import serializers

from pulp.app import models
from pulp.app.serializers import (MasterModelSerializer, ModelSerializer, DetailIdentityField,
                                  NotesKeyValueRelatedField, RepositoryRelatedField,
                                  ScratchpadKeyValueRelatedField, ContentRelatedField,
                                  ImporterRelatedField, PublisherRelatedField)


class RepositorySerializer(ModelSerializer):
    # _href is normally provided by the base class, but Repository's
    # "name" lookup field means _href must be explicitly declared.
    _href = serializers.HyperlinkedIdentityField(
        view_name='repositories-detail',
        lookup_field='name',
    )
    name = serializers.CharField(
        help_text=_('A unique name for this repository.'),
        write_only=True
    )

    description = serializers.CharField(
        help_text=_('An optional description.'),
        required=False
    )

    last_content_added = serializers.DateTimeField(
        help_text=_('Timestamp of the most recent addition of content to this repository.'),
        read_only=True
    )

    last_content_removed = serializers.DateTimeField(
        help_text=_('Timestamp of the most recent removal of content to this repository.'),
        read_only=True
    )
    notes = NotesKeyValueRelatedField()
    scratchpad = ScratchpadKeyValueRelatedField()
    importers = ImporterRelatedField(many=True)
    publishers = PublisherRelatedField(many=True)

    class Meta:
        model = models.Repository
        fields = ModelSerializer.Meta.fields + ('name', 'description', 'notes', 'scratchpad',
                                                'last_content_added', 'last_content_removed',
                                                'importers', 'publishers')


class ImporterSerializer(MasterModelSerializer):
    """
    Every importer defined by a plugin should have an Importer serializer that inherits from this
    class. Please import from `pulp.app.serializers` rather than from this module directly.
    """
    # _href is normally provided by the base class, but Importers's
    # "name" lookup field means _href must be explicitly declared.
    _href = DetailIdentityField()

    name = serializers.CharField(
        help_text=_('A name for this importer, unique within the associated repository.')
    )
    last_updated = serializers.DateTimeField(
        help_text='Timestamp of the most recent update of this configuration.',
        read_only=True
    )

    feed_url = serializers.CharField(
        help_text='The URL of an external content source.',
        required=False,
    )

    validate = serializers.BooleanField(
        help_text='Whether to validate imported content.',
        required=False,
    )

    ssl_ca_certificate = serializers.CharField(
        help_text='A PEM encoded CA certificate used to validate the server '
                  'certificate presented by the external source.',
        write_only=True,
        required=False,
    )
    ssl_client_certificate = serializers.CharField(
        help_text='A PEM encoded client certificate used for authentication.',
        write_only=True,
        required=False,
    )
    ssl_client_key = serializers.CharField(
        help_text='A PEM encoded private key used for authentication.',
        write_only=True,
        required=False,
    )
    ssl_validation = serializers.BooleanField(
        help_text='Indicates whether SSL peer validation must be performed.',
        required=False,
    )
    proxy_url = serializers.CharField(
        help_text='The optional proxy URL. Format: scheme://user:password@host:port',
        required=False,
    )
    basic_auth_user = serializers.CharField(
        help_text='The username to be used in HTTP basic authentication when syncing.',
        write_only=True,
        required=False,
    )
    basic_auth_password = serializers.CharField(
        help_text='The password to be used in HTTP basic authentication when syncing.',
        write_only=True,
        required=False,
    )
    download_policy = serializers.ChoiceField(
        help_text='The policy for downloading content.',
        allow_blank=False,
        choices=models.Importer.DOWNLOAD_POLICIES,
    )
    last_sync = serializers.DateTimeField(
        help_text='Timestamp of the most recent successful sync.',
        read_only=True
    )

    repository = RepositoryRelatedField()

    class Meta:
        abstract = True
        model = models.Importer
        fields = MasterModelSerializer.Meta.fields + (
            'name', 'last_updated', 'feed_url', 'validate', 'ssl_ca_certificate',
            'ssl_client_certificate', 'ssl_client_key', 'ssl_validation', 'proxy_url',
            'basic_auth_user', 'basic_auth_password', 'download_policy', 'last_sync', 'repository',
        )


class PublisherSerializer(MasterModelSerializer):
    """
    Every publisher defined by a plugin should have an Publisher serializer that inherits from this
    class. Please import from `pulp.app.serializers` rather than from this module directly.
    """
    # Every subclass must override the `_href` field with a `RepositoryNestedIdentityField` that
    # defines the view_name.
    _href = DetailIdentityField()
    name = serializers.CharField(
        help_text=_('A name for this publisher, unique within the associated repository.')
    )
    last_updated = serializers.DateTimeField(
        help_text=_('Timestamp of the most recent update of the publisher configuration.'),
        read_only=True
    )
    repository = RepositoryRelatedField()

    auto_publish = serializers.BooleanField(
        help_text=_('An indicaton that the automatic publish may happen when'
                    ' the repository content has changed.'),
        required=False
    )
    relative_path = serializers.CharField(
        help_text=_('The (relative) path component of the published url'),
        required=False
    )
    last_published = serializers.DateTimeField(
        help_text=_('Timestamp of the most recent successful publish.'),
        read_only=True
    )

    class Meta:
        abstract = True
        model = models.Publisher
        fields = MasterModelSerializer.Meta.fields + (
            'name', 'last_updated', 'repository', 'auto_publish', 'relative_path', 'last_published'
        )


class RepositoryContentSerializer(serializers.ModelSerializer):
    # RepositoryContentSerializer should not have it's own _href, so it subclasses
    # rest_framework.serializers.ModelSerializer instead of pulp.app.serializers.ModelSerializer
    content = ContentRelatedField()
    repository = RepositoryRelatedField()
    vadded = serializers.HyperlinkedRelatedField(view_name='repositoryversions-detail',
                                                 read_only=True)
    vremoved = serializers.HyperlinkedRelatedField(view_name='repositoryversions-detail',
                                                   read_only=True)

    class Meta:
        model = models.RepositoryContent
        fields = ('repository', 'content', 'vadded', 'vremoved')


class RepositoryVersionSerializer(ModelSerializer):
    _href = serializers.HyperlinkedIdentityField(
        view_name='repositoryversions-detail',
    )
    repository = RepositoryRelatedField()
    num = serializers.IntegerField(
        read_only=True
    )
    created = serializers.DateTimeField(
        help_text=_('Timestamp of creation.'),
        read_only=True
    )
    action = serializers.ChoiceField(
        help_text=_('The action that created this version.'),
        allow_blank=False,
        choices=models.RepositoryVersion.ACTIONS,
        read_only=True
    )

    class Meta:
        model = models.RepositoryVersion
        fields = ('_href', 'repository', 'num', 'created', 'action')
