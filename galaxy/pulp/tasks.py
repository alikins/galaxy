# (c) 2012-2019, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

import os
import tarfile
import tempfile
import shutil

from django.db import transaction
from galaxy.main import models
from pulpcore.app import models as pulp_models

from . import schema

import logging
log = logging.getLogger(__name__)


class VersionConflict(Exception):
    pass


def load_metadata(artifact):
    with tempfile.TemporaryDirectory() as td:
        temp_path = os.path.join(td, os.path.basename(artifact.file.path))
        shutil.copy(artifact.file.path, temp_path)
        with tarfile.open(temp_path, 'r') as pkg:
            # log.info('filenames: %s', pkg.getnames())
            for member in pkg.getmembers():
                # log.info('%s: %s', member.path.split('/'),
                #         member.path.split('/')[-1])
                if member.isfile() and \
                        member.path.split('/')[-1] == 'MANIFEST.json':
                    log.info('extracting %s from artifact', member)
                    meta_file = pkg.extractfile(member)
                    with meta_file:
                        return schema.CollectionArtifactManifest.parse(meta_file.read())
            log.warning('No metadata found for artifact=%s', artifact)


@transaction.atomic
def import_collection(artifact_pk, repository_pk):
    artifact = pulp_models.Artifact.objects.get(pk=artifact_pk)
    repository = pulp_models.Repository.objects.get(pk=repository_pk)

    meta = load_metadata(artifact)

    collection_info = meta.collection_info
    log.info('collection_info: %s type(): %s',
             collection_info, type(collection_info))
    # log.info('meta: %s', meta)
    collection, _ = models.Collection.objects.get_or_create(
        namespace=collection_info.namespace,
        name=collection_info.name,
    )
    collection_version, is_created = collection.versions.get_or_create(
        collection=collection,
        version=collection_info.version,
    )
    if not is_created:
        raise VersionConflict()

    relative_path = '{0}-{1}-{2}.tar.gz'.format(
        collection_info.namespace,
        collection_info.name,
        collection_info.version
    )
    pulp_models.ContentArtifact.objects.create(
        artifact=artifact,
        content=collection_version,
        relative_path=relative_path,
    )
    with pulp_models.RepositoryVersion.create(repository) as new_version:
        new_version.add_content(
            pulp_models.Content.objects.filter(pk=collection_version.pk)
        )

    publication = pulp_models.Publication.objects.create(
        repository_version=new_version,
        complete=True,
        pass_through=True,
    )
    pulp_models.Distribution.objects.update_or_create(
        name='galaxy',
        base_path='galaxy',
        defaults={'publication': publication},
    )
    log.info('Imported artifact: %s', relative_path)
