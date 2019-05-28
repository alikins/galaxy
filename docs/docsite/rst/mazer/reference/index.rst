.. _mazer_reference:

*********
Reference
*********

.. contents:: Topics


This topic provides a reference guide to Mazer CLI.

Optional Arguments
==================

Use the following optional arguments with the ``mazer`` command:

.. option:: -h, --help

Show help message and exit.

.. option:: -c, --ignore-certs

Ignores certificate validation errors when accessing the Galaxy server API.

.. option:: -s, --server-url

Provide the Galaxy server URL to use when accessing the API. For example, to use the Galaxy QA server, pass *https://galaxy-qa.ansible.com*.

.. option:: -v, --verbose

Run in verbose mode. Use *-vvv* for more, or *-vvvv* to enable connection debugging.

.. option:: --config

Provide a path to an alternate mazer config. Default is `~/.ansible/mazer.yml`.


Commands
========

Use ``mazer <command> --help`` to see help information for a specific command.

.. toctree::
   :maxdepth: 2

   build
   info
   install
   list
   migrate_role
   publish
   remove
   version

Environment variables
=====================

MAZER_HOME
    Set the paths where the mazer.yml and mazer-logging.yml config
    files are loaded from. The default is ~/.ansible.
