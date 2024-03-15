#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import platform

def get_kernel_version():
    kernel_ver_major = platform.version().split('.')[0]
    kernel_ver_minor = platform.version().split('.')[1]
    kernel_ver = f'{kernel_ver_major}.{kernel_ver_minor}'
    
    return kernel_ver

def get_build_number():
    return platform.version().split('.')[2]

def get_windows_version():
    kernel_ver = get_kernel_version()
    build_num = get_build_number()
    
    if (kernel_ver == '5.1') or (kernel_ver == '5.2'):
        return 'Windows XP'
    elif (kernel_ver == '6.0'):
        return 'Windows Vista'
    elif (kernel_ver == '6.1'):
        return 'Windows 7'
    elif (kernel_ver == '6.2'):
        return 'Windows 8'
    elif (kernel_ver == '6.3'):
        return 'Windows 8.1'
    elif (kernel_ver == '10.0'):
        if (int(build_num) < 22000):
            return 'Windows 10'
        elif (int(build_num) >= 22000) and (int(build_num) < 26000):
            return 'Windows 11'
        elif (int(build_num) >= 26000):
            return 'Windows 12'
        else:
            return f'NT {kernel_ver}'
    else:
        return f'NT {kernel_ver}'