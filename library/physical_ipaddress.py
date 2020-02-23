import os
import subprocess
from ansible.module_utils.basic import AnsibleModule


EXAMPLES = '''
- name: Test module
  physical_ipaddress:
'''


def get_physical_interfaces():
    interface_dir = "/sys/class/net/"
    physical_interfaces = []
    interfaces = os.listdir(interface_dir)
    for i in interfaces:
        interfaces_fullpath = interface_dir + i
        if os.path.islink(interfaces_fullpath):
            if 'virtual' not in os.readlink(interfaces_fullpath):
                physical_interfaces.append(i)
    return physical_interfaces


def get_interface_ipaddrress(interface):
    cmd = r"ip addr show dev %s|grep -Po 'inet \K[\d\.]+'" % interface
    try:
        result = subprocess.check_output(
                     cmd,
                     shell=True).rstrip().split('\n')
    except Exception:
        result = []
    return result


def run_module():
    result = dict(
        changed=False,
        ips='',
    )

    module_args = dict()

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    pyhsical_interfaces = get_physical_interfaces()
    ips = []

    for physical_interface in pyhsical_interfaces:
        for ip in get_interface_ipaddrress(physical_interface):
            ips.append(ip)

    result['ips'] = ips

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
