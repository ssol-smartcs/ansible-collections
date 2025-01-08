# SEIKO SmartCS Ansible Collection

## Description

SmartCS modules for Ansible works sends and receives character string to devices connected to SmartCS, and configures and manages SmartCS.

## Requirements

- Ansible Core 2.16.0 to 2.18.x
- Python 3.10 or above

## Installation
Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```
ansible-galaxy collection install seiko.smartcs
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
collections:
  - name: seiko.smartcs
```

**Note**: that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```
ansible-galaxy collection install seiko.smartcs --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version 1.6.0:

```
ansible-galaxy collection install seiko.smartcs:==1.6.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Use Cases

### Use Case 1 - Login to Network Device via Console Server SmartCS and execute "show version"
You can call modules by their Fully Qualified Collection Namespace (FQCN), such as seiko.smartcs.smartcs_tty_command. The following example task login to the console port of the network device via Console Server SmartCS and execute the show version command, using the FQCN:
```
---
- name: Login to Network Device via Console Server SmartCS and execute "show version"
  seiko.smartcs.smartcs_tty_command:
    tty: 1
    cmd_timeout: 5
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

### Use Case 2 - Set and write the transmission speed and label of SmartCS serial port 20
```
---
- name: configuration tty 20 settings and write
  seiko.smartcs.smartcs_config:
    lines:
      - set pord tty 20 label ROUTER
      - set tty 20 baud 19200
    save_when: modified
```

### Use Case 3 - Displays the SmartCS hardware configuration, system software version, and boot information.
```
- name: run show version on remote devices
  seiko.smartcs.smartcs_command:
    commands: show version
```

## Testing
Tested with Ansible Core v2.16+ Ansible Core versions prior to 2.16 are not supported.
This collection has been tested against NS-2250 Ver 3.1.1

## Support
For any support request, please reach out to [SmartCS Support Portal](https://www.seiko-sol.co.jp/en/products/console-server/console-server_faq/).

## Release Notes and Roadmap
Please see the [release notes](https://github.com/ssol-smartcs/ansible-collections/blob/main/seiko.smartcs/CHANGELOG.rst) for the latest updates to the SmartCS  collection.

## Related Information
See example playbooks and use cases [here](https://github.com/ssol-smartcs/ansible-tech-info/blob/main/contents/playbook-example.md). 
### SmartCS Official Website (SEIKO SOLUTIONS INC.)

- [Network automation with Ansible](https://www.seiko-sol.co.jp/en/products/console-server/console-server_automation/ansible/)
- [AnsibleとSmartCSの連携](https://www.seiko-sol.co.jp/products/console-server/console-server_automation/ansible/)


## License Information
SmartCS modules for Ansible is licensed under the [GNU General Public License Version 3](https://www.gnu.org/licenses/gpl-3.0.html).
This software includes programs which are modified from Ansible.
For the full text, see the COPYING file.
