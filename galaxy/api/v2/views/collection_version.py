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

from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from galaxy.main import models
from galaxy.api.v2 import serializers
from galaxy.api.v2.pagination import CustomPagination


__all__ = (
    'VersionListView',
    'VersionDetailView',
)


# TODO(awcrosby): Move to views/utils.py and reuse across views
def _lookup_collection(kwargs):
    """Helper method to get collection from id, or namespace and name."""
    pk = kwargs.get('pk', None)
    ns_name = kwargs.get('namespace', None)
    name = kwargs.get('name', None)

    if pk:
        return get_object_or_404(models.Collection, pk=pk)

    ns = get_object_or_404(models.Namespace, name=ns_name)
    return get_object_or_404(models.Collection, namespace=ns, name=name)


class VersionListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.VersionSummarySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """Return list of versions for a specific collection."""
        collection = _lookup_collection(self.kwargs)
        return models.CollectionVersion.objects.filter(collection=collection)


class VersionDetailView(views.APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        """Return a collection version."""
        version = self._get_version(kwargs)
        serializer = serializers.VersionDetailSerializer(version)
        return Response(serializer.data)

    def _get_version(self, kwargs):
        """
        Get collection version from either version id, or from
        collection namespace, collection name, and version string.
        """
        version_pk = kwargs.get('version_pk', None)
        version_str = kwargs.get('version', None)
        if version_pk:
            return get_object_or_404(models.CollectionVersion, pk=version_pk)
        else:
            collection = _lookup_collection(kwargs)
            return get_object_or_404(
                models.CollectionVersion,
                collection=collection,
                version=version_str,
            )
