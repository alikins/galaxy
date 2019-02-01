import json
import re

import attr
import semantic_version as semver


_FILENAME_RE = re.compile(
    r'^(?P<namespace>\w+)-(?P<name>\w+)-'
    r'(?P<version>[0-9a-zA-Z.+-]+)\.tar\.gz$'
)
_NAME_RE = re.compile(r'^[0-9a-z_]+$')


@attr.s(slots=True)
class CollectionFilename(object):

    namespace = attr.ib()
    name = attr.ib()
    version = attr.ib(converter=semver.Version)

    @classmethod
    def parse(cls, filename):
        match = _FILENAME_RE.match(filename)
        if not match:
            raise ValueError(
                'Invalid filename. Expected: '
                '{namespace}-{name}-{version}.tar.gz'
            )

        return cls(**match.groupdict())

    @namespace.validator
    @name.validator
    def _validator(self, attribute, value):
        if not _NAME_RE.match(value):
            raise ValueError(
                'Invalid {0}: {1!r}'.format(attribute.name, value)
            )


@attr.s(frozen=True)
class CollectionInfo(object):
    namespace = attr.ib()
    name = attr.ib()
    version = attr.ib()
    license = attr.ib()
    description = attr.ib(default=None)

    repository = attr.ib(default=None)
    documentation = attr.ib(default=None)
    homepage = attr.ib(default=None)
    issues = attr.ib(default=None)

    authors = attr.ib(factory=list)
    tags = attr.ib(factory=list)
    readme = attr.ib(default='README.md')

    # Note galaxy.yml 'dependencies' field is what mazer and ansible
    # consider 'requirements'. ie, install time requirements.
    dependencies = attr.ib(factory=list)

    @property
    def label(self):
        return '%s.%s' % (self.namespace, self.name)


@attr.s(frozen=True)
class CollectionArtifactManifest(object):
    collection_info = attr.ib(type=CollectionInfo)
    format = attr.ib(default=1)

    # files = attr.ib(factory=list,
    # converter=convert_list_to_artifact_file_list)
    files = attr.ib(factory=list)

    @classmethod
    def parse(cls, data):
        meta = json.loads(data)
        col_info = meta.pop('collection_info', None)
        meta['collection_info'] = CollectionInfo(**col_info)
        return cls(**meta)


@attr.s(frozen=True, slots=True, kw_only=True)
class Metadata:
    """Ansible Collection metadata."""
    namespace = attr.ib()
    name = attr.ib()
    version = attr.ib(converter=semver.Version)

    author = attr.ib(default='')
    author_email = attr.ib(default='')

    @name.validator
    @namespace.validator
    def _validate_name(self, attribute, value):
        if not _NAME_RE.match(value):
            raise ValueError('Invalid "{0}" attribute'.format(attribute))

    @classmethod
    def parse(cls, data):
        meta = json.loads(data)
        return cls(**meta)
