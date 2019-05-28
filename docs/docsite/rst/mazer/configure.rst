
.. _mazer_configure:

***********
Configuring
***********

.. contents:: Topics


This topic provides instructions on configuring Mazer CLI.

mazer.yml
---------

Configure Mazer by creating ``~/.ansible/mazer.yml``, a YAML formated file, on the local file sytem. The following shows
an example configuration file:

.. code-block:: yaml

    version: 1
    server:
      ignore_certs: false
      url: https://galaxy-qa.ansible.com
      api_key: da39a3ee5e6b4b0d3255bfef95601890afd80709
    collections_path: ~/.ansible/collections
    global_collections_path: /usr/share/ansible/collections

version
    The configuration format version. Defaults to 1.

server
    Provide Galaxy server connection information, including: url and ignore certs.

    Set the value of *url* to the Galaxy server address, and the *ignore_certs* to either *true* or *false*. When
    set to *true*, Mazer will not attempt to verify the server's TLS certificates.

    *api_key* is the API key used when mazer needs to authenticate to the Galaxy API. *api_key* here is equilivent to the cli '--api-key'.
    The API key can be found at https://galaxy.ansible.com/me/preferences

collections_path
    Provide a path to a directory on the local filesytem where Ansible collections will be installed.
    Defaults to ``~/.ansible/collections``

global_collections_path
    Provide a path to a directory on the local filesytem where Ansible collections will be installed when using the '--global' cli option.
    Defaults to ``/usr/share/ansible/collections``

