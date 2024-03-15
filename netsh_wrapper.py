#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess

class Netsh:
    def __init__(self, netsh_path, xml_target_dir, wifi_profile_template) -> None:
        self.netsh_path = netsh_path
        self.xml_target_dir = xml_target_dir
        self.wifi_profile_template = wifi_profile_template
        return

    def _run_cmd(self, cmd: str = None):
        result = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True, text = True)
        
        return result

    def get_wlan_interface_state(self):
        result = self._run_cmd(f'{self.netsh_path} wlan show drivers')
        
        if ('wi-fi' in result.stdout.lower()) and ('.inf' in result.stdout.lower()):
            return {'state': 'INTERFACE_UP', 'run_result': result}
        
        if ('wlansvc' in result.stdout.lower()):
            return {'state': 'ERR_SERVICE', 'run_result': result}
        
        return {'state': 'ERR_INTERFACE', 'run_result': result}

    def generate_profile_xml(self, name: str, hex: str, server_name: str):
        fname = os.path.join(self.xml_target_dir, f'{name}.xml')
        f = open(fname, 'w')
        f.write(self.wifi_profile_template.substitute(name=name, hex=hex, server_name=server_name))
        f.close()
        return

    def disconnect(self):
        result = self._run_cmd(f'{self.netsh_path} wlan disconnect')
        return result

    def del_profile(self, profile_name: str):
        result = self._run_cmd(f'{self.netsh_path} wlan delete profile "{profile_name}"')
        return result

    def add_profile(self, xml_path: str):
        result = self._run_cmd(f'{self.netsh_path} wlan add profile filename="{xml_path}"')
        return result