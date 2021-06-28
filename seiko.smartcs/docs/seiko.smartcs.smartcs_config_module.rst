.. _seiko.smartcs.smartcs_config_module:


****************************
seiko.smartcs.smartcs_config
****************************

**Manage configuratin sections of SmartCS**


Version added: 1.3.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module provides configuration of SmartCS. If there is a difference between running configration and a command specfied by the lines option, execute configration command.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>backup</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>This argument will cause the module to create a full backup of the current <code>running-config</code> from the remote device before any changes are made. If the <code>backup_options</code> value is not given, the backup file is written to the <code>backup</code> folder in the playbook root directory or role root directory, if playbook is part of an ansible role. If the directory does not exist, it is created.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>lines</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The ordered set of commands that should be configured in the section. The commands must be the exact same commands as found in the device running-config.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: commands</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>match</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>line</b>&nbsp;&larr;</div></li>
                                    <li>none</li>
                        </ul>
                </td>
                <td>
                        <div>Instructs the module on the way to perform the matching of the set of commands against the current device config.  If match is set to <em>line</em>, commands are matched line by line. if match is set to <em>none</em>, the module will not attempt to compare the source configuration with the running configuration on the remote device.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>save_when</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>always</li>
                                    <li><div style="color: blue"><b>never</b>&nbsp;&larr;</div></li>
                                    <li>modified</li>
                                    <li>changed</li>
                        </ul>
                </td>
                <td>
                        <div>When changes are made to the device running-configuration, the changes are not copied to non-volatile storage by default.  Using this argument will change that before.  If the argument is set to <em>always</em>, then the running-configratoin will always be copied to the startup-configration and the <em>modified</em> flag will always be set to True.  If the argument is set to <em>modified</em>, then the running-configration will only be copied to the startup-configration if it has changed since the last save to startup-configration.  If the argument is set to <em>never</em>, the running-configration will never be copied to the startup-configration.  If the argument is set to <em>changed</em>, then the running-configration will only be copied to the startup-configration if the task has made a change.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>src</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specifies the source path to the file that contains the configuration to load.  The path to the source file can either be the full path on the Ansible control host or a relative path from the playbook or role root directory.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - Tested against SmartCS NS-2250 System Software Ver 2.1



Examples
--------

.. code-block:: yaml

    - name: configuration tty 1 settings
      seiko.smartcs.smartcs_config:
        lines:
        - pord tty 1 label SWITCH_1
        - set tty 1 baud 38400

    - name: configuration tty 20 settings and write
      seiko.smartcs.smartcs_config:
        lines:
        - set pord tty 20 label ROUTER
        - set tty 20 baud 19200
        save_when: modified

    - name: configuration host name and get backup file
      seiko.smartcs.smartcs_config:
        lines:
        - set hostname SmartCS_TEST1
        save_when: always
        backup: yes



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>backup_path</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                    </div>
                </td>
                <td>when backup is yes</td>
                <td>
                            <div>The full path to the backup file</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">/playbooks/ansible/backup/smartcs_config.2019-03-16@16:00:16</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>commands</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The set of commands that will be pushed to the remote device</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[&#x27;set hostname NS-2250-48&#x27;, &#x27;set tty 1 baud 19200&#x27;]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>updates</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The set of commands that will be pushed to the remote device</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[&#x27;set hostname NS-2250-48&#x27;, &#x27;set tty 1 baud 19200&#x27;]</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Seiko Solutions Inc. (@naka-shin1)
