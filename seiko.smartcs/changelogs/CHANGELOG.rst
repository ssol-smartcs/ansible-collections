==================================================
SEIKO SmartCS Collection and Modules Release Notes
==================================================

.. contents:: Topics

v1.4.1
======

Release Date
---------------

- 2021.9

Release Summary
---------------

- Extended the supported versions of ansible 2.9 series.
- Improved errors detected by ansible-test sanity.


v1.4.0
======

Release Date
---------------

- 2021.6

Release Summary
---------------

- Added support for ansible-core 2.11 series.
- Added support for ansible 2.9 series.
- Improved errors detected by ansible-test sanity
- Minor changes to README.md
- Fix documentation section of cliconf


v1.3.0
======

Release Date
---------------

- 2021.4

Release Summary
---------------

- Added support for Ansible Collections.
- Added support for Ansible 2.10 series.


v1.2.0
======

Release Date
---------------

- 2021.1

Release Summary
---------------

- Added support for Ansible 2.9 series.
- Bug fixes

Bugfixes
--------

smartcs_facts
^^^^^^^^^^^^^
- Fix the bug when tty is specified in gather_subset option
- Fix the bug that interface information can't be obtained correctly.


v1.1.1
======

Release Date
---------------

- 2021.1

Release Summary
---------------

- Bug fixes for version 1.1.0

Bugfixes
--------

smartcs_facts
^^^^^^^^^^^^^
- Fix the bug when tty is specified in gather_subset option
- Fix the bug that interface information can't be obtained correctly.


v1.1.0
======

Release Date
---------------

- 2019.10

Release Summary
---------------

- Added support for Ansible 2.8 series.
- Added functionality to existing modules.
- Bug fixes

Minor Changes
-------------

smartcs_tty_command
^^^^^^^^^^^^^^^^^^^
- Add option to specify send string as external file
- Add more strings that can be specified with sendchar
- Add a function to check console status before sending a string
- Add the ability to output customized return values

Bugfixes
--------

- Fix a bug that playbook doesn't work properly when smartcs SW is working on the backup side
- Fix ansible-doc command error

smartcs_tty_command
^^^^^^^^^^^^^^^^^^^
- Fixed a bug about sendchar



v1.0.0
======

Release Date
---------------

- 2019.3

Release Summary
---------------

- Initial release of Ansible Modules for SmartCS 
- Added support for Ansible 2.8 series.

New Modules
-----------

- smartcs_command - Run commands on remote devices running SmartCS
- smartcs_config - Manage configuratin sections of SmartCS
- smartcs_facts - Collect facts from SmartCS
- smartcs_tty_command - Send character string to device via ConsoleServer SmartCS