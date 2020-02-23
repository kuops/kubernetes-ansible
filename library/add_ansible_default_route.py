import subprocess
from ansible.module_utils.basic import AnsibleModule


class AnsibleDefaultRoute:
    def __init__(self, interface):
        self.interface = interface

    def check_default_route(self):
        check_cmd = r'ip route|grep 8.8.8.8'
        try:
            subprocess.check_output(check_cmd, shell=True,)
            return True
        except Exception:
            return False

    def add_default_route(self):
        add_cmd = r'ip route add 8.8.8.8 dev %s' % self.interface
        proc = subprocess.Popen(
            add_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if proc.returncode == 0:
            return True, output.rstrip().decode('utf-8')
        else:
            return False, error.rstrip().decode('utf-8')

    def remove_default_route(self):
        remove_cmd = r'ip route del 8.8.8.8'
        proc = subprocess.Popen(
            remove_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if proc.returncode == 0:
            return True, output.rstrip().decode('utf-8')
        else:
            return False, error.rstrip().decode('utf-8')


def run_module():
    result = dict(
        changed=False,
        msg=''
    )

    module_args = dict(
        ifname=dict(type='str', required=True),
        add=dict(type='bool', required=False, default=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    dr = AnsibleDefaultRoute(module.params['ifname'])
    if module_args['add']:
        if not dr.check_default_route():
            add_result, add_msg = dr.add_default_route()
            result['msg'] = add_msg
            if add_result:
                result['changed'] = True
            else:
                module.fail_json(**result)
        else:
            result['msg'] = 'route exists.'
    else:
        if dr.check_default_route():
            remove_result, remove_msg = dr.remove_default_route()
            result['msg'] = remove_msg
            if remove_result:
                result['changed'] = True
            else:
                module.fail_json(**result)
        else:
            result['msg'] = 'route removed.'

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
