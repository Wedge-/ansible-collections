#! /usr/bin/python
# -*- config: utf-8 -*-
# Copyright (c) 2025, Aymeric Roynette <wedge.ant@gmail.com>
# GPL-3.0

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: apache2_site
author:
    - Aymeric Roynette
short_description: Enables/Disables a site of the Apache2 webserver using a2ensite/a2dissite
description:
    - Enables/Disables a site of the Apache2 webserver using a2ensite/a2dissite
extends_documentation_fragmetn:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    name:
        type: str
        description:
            - Name of the site file conf (without .conf extension) to enable/disable as given to C(a2ensite)/C(a2dissite)
        required: true
    state:
        type: str
        description:
            - Desired state of the site
        choices: ['present', 'absent']
        default: present
requirements: ["a2ensite", "a2dissite"]
notes:
    - This does only work on Debian-based distributions or other Linux distributions that ship the C(a2ensite)/C(a2dissite) tools
"""

EXAMPLES = r"""
- name: Enable the foo.conf site file
  apache2_site:
    name: foo
    state: present

- name: Disable the 000-default.conf site file
  apache2_site:
    name: 000-default
    state: absent
"""

RETURN = r"""
result:
    description: Message about action taken
    returned: always
    type: str
"""

import re
from ansible.module_utils.basic import AnsibleModule

def _set_state(module, state):
    name = module.params['name']
    want_enabled = state == 'present'
    state_string = {'present': 'enabled', 'absent': 'disabled'}[state]
    a2site_binary = {'present': 'a2ensite', 'absent': 'a2dissite'}[state]
    a2site_binary_path = module.get_bin_path(a2site_binary)

    if module.check_mode:
        success_msg = "Site %s %s" % (name, state_string)
        module.exit_json(changed=True, result=success_msg)

    if a2site_binary_path is None:
        module.fail_json(msg="%s not found !" (a2site_binary))

    a2site_binary_cmd = [a2site_binary_path]
    result, stdout, stderr = module.run_command(a2site_binary_cmd + [name])
    success_msg = "%s" % (stdout.split('\n')[0])
    error_msg = "%s" % (stderr.split('\n')[0])

    if re.search("Site %s already" % name, stdout):
        module.exit_json(changed=False, result=success_msg)
    elif re.search("Enabling site %s" % name, stdout):
        module.exit_json(changed=True, result=success_msg)
    elif re.search("ERROR: Site %s does not exist" % name, stderr):
        module.exit_json(skipped=True, result=error_msg)
    else:
        module.exit_json(skipped=True, result=error_msg)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True
    )

    if module.params['state'] in ['present', 'absent']:
        _set_state(module, module.params['state'])

if __name__ == '__main__':
    main()
