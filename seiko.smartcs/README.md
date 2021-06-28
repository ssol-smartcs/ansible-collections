# SEIKO SmartCS Ansible Collection

SmartCS modules for Ansible works sends and receives character string to devices connected to SmartCS, and configures and manages SmartCS.

This software works as a module of [Ansible](https://ansible.com) by Red Hat, Inc.

## SmartCS software version compatibility

This collection has been tested against NS-2250 Ver 2.1


<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.10,<2.11**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->


### Supported connections
The SEIKO SmartCS collection supports ``network_cli``  connections


## Included content

<!--start collection content-->
### Cliconf plugins
Name | Description
--- | ---
[seiko.smartcs.smartcs](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/docs/seiko.smartcs.smartcs_cliconf.rst)|Use smartcs cliconf to run command on SmartCS platform

### Modules
Name | Description
--- | ---
[seiko.smartcs.smartcs_command](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/docs/seiko.smartcs.smartcs_command_module.rst)|Run commands on remote devices running SmartCS
[seiko.smartcs.smartcs_config](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/docs/seiko.smartcs.smartcs_config_module.rst)|Manage configuratin sections of SmartCS
[seiko.smartcs.smartcs_facts](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/docs/seiko.smartcs.smartcs_facts_module.rst)|Collect facts from SmartCS
[seiko.smartcs.smartcs_tty_command](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/docs/seiko.smartcs.smartcs_tty_command_module.rst)|Send character string to device via ConsoleServer SmartCS

<!--end collection content-->

## Installing this collection

### Installation
You can install the SEIKO SmartCS collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install seiko.smartcs

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: seiko.smartcs
```

### See Also:

* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.


## Playbook 

### Using modules from the SEIKO SmartCS collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `seiko.smartcs.smartcs_tty_command`.
The following example task login to the console port of the network device via Console Server SmartCS and execute the show version command, using the FQCN:

```yaml
---
- name: Login to Network Device via Console Server SmartCS and execute "show version"
  seiko.smartcs.smartcs_tty_command:
    tty: 1
    cmd_timeout : 5
    recvchar:
    - 'login: '
    - 'Password: '
    - 'SWITCH> '
    sendchar:
    - __NL__
    - user1
    - secret
    - show version
    - exit
```


## Release notes
<!--Add a link to a changelog.md file or an external docsite to cover this information. -->
Release notes are available [here](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/changelogs/CHANGELOG.rst).


## Authors

SmartCS modules for Ansible is created by [SEIKO SOLUTIONS INC.](https://www.seiko-sol.co.jp/).


## License

SmartCS modules for Ansible is licensed under the [GNU General Public License Version 3](https://www.gnu.org/licenses/gpl-3.0.html).

This software includes programs which are modified from Ansible.
For the full text, see the COPYING file.


## Building Ansible Collections Package for SmartCS

```
$ git clone https://github.com/ssol-smartcs/ansible-collections
$ cd ansible-collections
$
$ ansible-galaxy collection build seiko.smartcs
$
```


## More information

- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Galaxy User guide](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html)
- [Ansible Network Getting Started](https://docs.ansible.com/ansible/latest/network/getting_started/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
