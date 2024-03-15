#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import string
import time
import ctypes
import gettext
from rich.console import Console
from pyfiglet import Figlet

from platform_info import get_kernel_version, get_build_number, get_windows_version
from netsh_wrapper import Netsh
from error import *
from string_res import StringRsc



APP_NAME = 'Yonsei Secure Wi-Fi Profile Installer'
PACKAGE_NAME = 'Yonsei-WiFi-Profile-Installer'
APP_VER = '1.0 BETA'
APP_AUTHOR = 'kimiroo'

MINIMUM_KERNEL_VER = 6.2

WIFI_PROFILE_TEMPLATE = string.Template('<?xml version="1.0"?><WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1"><name>$name</name><SSIDConfig><SSID><hex>$hex</hex><name>$name</name></SSID><nonBroadcast>false</nonBroadcast></SSIDConfig><connectionType>ESS</connectionType><connectionMode>auto</connectionMode><autoSwitch>false</autoSwitch><MSM><security><authEncryption><authentication>WPA2</authentication><encryption>AES</encryption><useOneX>true</useOneX><FIPSMode xmlns="http://www.microsoft.com/networking/WLAN/profile/v2">false</FIPSMode></authEncryption><PMKCacheMode>enabled</PMKCacheMode><PMKCacheTTL>720</PMKCacheTTL><PMKCacheSize>128</PMKCacheSize><preAuthMode>disabled</preAuthMode><OneX xmlns="http://www.microsoft.com/networking/OneX/v1"><cacheUserData>true</cacheUserData><authMode>user</authMode><EAPConfig><EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><EapMethod><Type xmlns="http://www.microsoft.com/provisioning/EapCommon">21</Type><VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId><VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType><AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">311</AuthorId></EapMethod><Config xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><EapTtls xmlns="http://www.microsoft.com/provisioning/EapTtlsConnectionPropertiesV1"><ServerValidation><ServerNames>$server_name</ServerNames><DisablePrompt>false</DisablePrompt></ServerValidation><Phase2Authentication><PAPAuthentication/></Phase2Authentication><Phase1Identity><IdentityPrivacy>false</IdentityPrivacy></Phase1Identity></EapTtls></Config></EapHostConfig></EAPConfig></OneX></security></MSM></WLANProfile>')
WIFI_DETAILS_YONSEI = {
    'name': 'Yonsei',
    'hex': '596F6E736569',
    'server_name': 'yonsei.ac.kr'
}
WIFI_DETAILS_EDUROAM = {
    'name': 'eduroam',
    'hex': '656475726F616D',
    'server_name': ''
}
WIFI_PROVISION_LIST = [WIFI_DETAILS_YONSEI, WIFI_DETAILS_EDUROAM]
WIFI_PROFILE_DELETE_TARGETS = ['Yonsei', 'Yonsei_Setup', 'eduroam']

NETSH_PATH = 'C:\\Windows\\System32\\netsh.exe'
XML_TARGET_DIR = os.path.dirname(os.path.realpath(__file__))
IS_DEBUG = False



### Script-wide init

# Check support for unicode special char.
try:
    '✓✗'.encode(sys.stdout.encoding)
    is_unicode = True
except UnicodeEncodeError:
    is_unicode = False

# fallback to alt. symbol if not supported
check_mark = '✓' if (is_unicode) else '√'
cross_mark = '✗' if (is_unicode) else 'X'

# Load custom rich printing module 
console = Console(highlight=False)
# Load external translation module
s = StringRsc()
# Set terminal title
ctypes.windll.kernel32.SetConsoleTitleW(APP_NAME)
# Load netsh wrapper module
netsh = Netsh(netsh_path=NETSH_PATH,
                xml_target_dir=XML_TARGET_DIR,
                wifi_profile_template=WIFI_PROFILE_TEMPLATE)


### Rich_Print
def r_print(msg: str, type: str = '', end='\n'):
    if (type == 'title'):
        console.print(f'*** {msg}', end=end)
    elif (type == 'log'):
        console.print(f'[bright_black]  - {msg}[/bright_black]', end=end)
    elif (type == 'log_bright'):
        console.print(f'  - {msg}', end=end)
    elif (type == 'success'):
        console.print(f'  [bold bright_green]{check_mark} {msg}[/bold bright_green]\n\n', end=end)
    elif (type == 'fail'):
        console.print(f'  [bold bright_red]{cross_mark} {msg}[/bold bright_red]\n\n', end=end)
    else:
        console.print(msg, end=end)
    return


def is_user_ignore_error():
    r_print(f'{s.ONE_OR_MORE_ERROR} {s.THIS_MAY_CAUSE_ADDITIONAL}')
    
    user_input = ''
    while True:
        user_input = input(f'{s.IGNORE_AND_CONTINUE} [Y/n]: ')
        
        if (user_input.lower() == 'y'):
            r_print(s.CONTINUING_INSTALL, type='log')
            return True

        elif (user_input.lower() == 'n'):
            r_print(s.CONTINUING_INSTALL, type='log')
            return False

        else:
            r_print(f'{s.IS_NOT_VALID_INPUT.format(user_input)}\n')
            pass


def print_err_msg(msg: str = ''):
    # Clean up message (Remove blank lines)
    msg = []
    new_msg = ''
    try:
        msg = msg.splitlines()
    except:
        pass
    
    for line in msg:
        if (line != ''):
            new_msg += line
            new_msg += '\n'
    
    # Set new_msg to 'None' if none
    new_msg = f'{s.NONE}\n' if (new_msg == '') else new_msg
    
    # Print message
    r_print('')
    r_print(s.ERROR_MESSAGE)
    r_print(new_msg)


def print_exception_msg(msg:str = '', desc:str = ''):
    # Prefix
    r_print('='*82 + '\n')
    r_print(f'[bright_red]{s.INSTALLATION_FAILED}[/bright_red]\n')
    r_print(f'{s.ONE_OR_MORE_ERROR}:\n')
    
    # Main msg
    r_print(f'[bold bright_white]{msg}[bold bright_white]\n')
    
    # Desc
    r_print(f'{desc}\n')
    
    # Suffix
    r_print(f'{s.CANNOT_CONTINUE}')
    r_print(f'{s.IF_PROBLEM_CONTINUES}')
    
    return


def pause_for_keys():
    os.system('pause >nul')
    return


def main():
    ### Init main func
    is_error_occured = False
    is_error_occured_in_current_scope = False
        
    ### Print intro
    text_yonsei = str(Figlet(font='roman').renderText('   Yonsei'))
    text_wifi = Figlet(font='roman').renderText('    Wi-Fi')
    text_app_info = f'{APP_NAME} (Version: {APP_VER}) by {APP_AUTHOR}'
    
    r_print('')
    r_print(f'[bold bright_blue]{text_yonsei}[/bold bright_blue]')
    r_print(f'[bold bright_white]{text_wifi}[/bold bright_white]')
    r_print(f'{' '*7}[bright_black]{text_app_info}[/bright_black]\n')
    
    r_print('='*82 + '\n')
    
    r_print(s.CLOSE_ALL_APPS_AND_REFRAIN)
    r_print(s.WILL_BEGIN_IN_FIVE)
    
    time.sleep(5)
    
    r_print('')
    r_print(s.STARTING_INSTALL)
    r_print('')
    
    time.sleep(2)
    
    r_print('-'*82 + '\n\n')
    

    ### Check system version
    r_print(s.CHECKING_SYS_REQ, type='title')
    
    if (platform.system().lower() != 'windows'):
        r_print(s.DETECTED_OS_OTHER.format(platform.platform()), type='log')
        r_print(s.UNSUPPORTED_PLATFORM, type='log')
        raise UnsupportedPlatformError({'platform_info': platform.platform()})
    
    kernel_ver = get_kernel_version()
    build_num = get_build_number()
    windows_ver = get_windows_version()
    
    r_print(s.DETECTED_OS.format(windows_ver, build_num), type='log')
    
    if (float(kernel_ver) < MINIMUM_KERNEL_VER):
        r_print(s.WIN_VER_TOO_LOW, type='log')
        r_print(s.FAIL, type='fail')
        raise UnsupportedVersionError({'platform_info': windows_ver})
    else:
        r_print(s.SUCCESS, type='success')
    
    

    ### Check interface state
    r_print(s.CHECKING_WLAN_IFACE, type='title')
    
    wlan_result = netsh.get_wlan_interface_state()
    r_print(s.INTERFACE_STATE.format(wlan_result['state']), type='log')
    
    if (wlan_result['state'] == 'ERR_SERVICE'):
        r_print(s.SVC_NOT_RUNNING, type='log')
        r_print(s.FAIL, type='fail')
        raise WirelessServiceError({})
    
    elif (wlan_result['state'] == 'ERR_INTERFACE'):
        r_print(s.WLAN_IFACE_NOTFOUND, type='log')
        r_print(s.FAIL, type='fail')
        raise WirelessInterfaceError({})
    
    r_print(s.WLAN_IFACE_NORMAL, type='log')
    r_print(s.SUCCESS, type='success')
    


    ### Initialize wireless interface
    r_print(s.PREPARING_WLAN_IFACE, type='title')
    r_print(s.DISCONNECTING_WIFI, type='log', end='')
    
    result_disconnect = netsh.disconnect()
    
    if (result_disconnect.returncode == 0):
        r_print(f' [green]{s.DONE}[/green]')
        r_print(s.SUCCESS, type='success')

    else:
        r_print(f' [red]{s.FAILED}[/red]')
        r_print(s.FAIL, type='fail')
        
        # Print shell output
        print_err_msg(result_disconnect.stdout + result_disconnect.stderr)
        
        # Ask user whether to continue or not
        if not(is_user_ignore_error()):
            raise InterfaceResetError({})
        
        is_error_occured = True
    
    

    ### Delete old wlan profiles
    r_print(s.DELETING_OLD_PROFILES, type='title')
    is_error_occured_in_current_scope = False
    
    for profile_name in WIFI_PROFILE_DELETE_TARGETS:
        r_print(s.DELETING_PROFILE_NAME.format(profile_name), type='log', end='')
        
        result_del_profile = netsh.del_profile(profile_name=profile_name)
        
        if (result_del_profile.returncode == 0):
            r_print(f' [green]{s.DONE}[/green]', type='print')

        else:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(f' [red]{s.FAILED}[/red]', type='print')
            
            print_err_msg(result_del_profile.stdout + result_del_profile.stderr)
            
            if not(is_user_ignore_error()):
                r_print(s.FAIL, type='fail')
                raise ProfileDeletionError({})
    
    if is_error_occured_in_current_scope:
        r_print(s.FAIL, type='fail')
    else:
        r_print(s.SUCCESS, type='success')
    
    

    ### Generate wlan profile xml files
    r_print(s.GENERATING_NEW_PROFILES, type='title')
    
    for profile in WIFI_PROVISION_LIST:
        r_print(s.GENERATING_PROFILE_NAME.format(profile['name']), type='log', end='')
        
        try:
            netsh.generate_profile_xml(name=profile['name'], hex=profile['hex'], server_name=profile['server_name'])
            
        except IOError as e:
            r_print(f' [red]{s.FAILED}[/red]', type='print')
            r_print(s.FAIL, type='fail')
            raise IOError({'msg': e, 'on_event': 'GenerateProfile'})

        except Exception as e:
            r_print(f' [red]{s.FAILED}[/red]', type='print')
            r_print(s.FAIL, type='fail')
            raise Exception({'msg': e, 'on_event': 'GenerateProfile'})

        else:
            r_print(f' [green]{s.DONE}[/green]', type='print')
    
    r_print(s.SUCCESS, type='success')
    
    

    ### Adding wlan profile xml files via netsh
    r_print(s.ADDING_NEW_PROFILES, type='title')
    is_error_occured_in_current_scope = False
    
    for profile in WIFI_PROVISION_LIST:
        r_print(s.ADDING_PROFILE_NAME.format(profile['name']), type='log', end='')
        
        fpath = os.path.join(XML_TARGET_DIR, f'{profile['name']}.xml')
        result_add_profile = netsh.add_profile(f'"{fpath}"')
        
        if (result_add_profile.returncode == 0):
            r_print(f' [green]{s.DONE}[/green]', type='print')

        else:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(f' [red]{s.FAILED}[/red]', type='print')
            
            # Print shell output
            print_err_msg(result_add_profile.stdout + result_add_profile.stderr)
            
            # Ask user whether to continue or not
            if not(is_user_ignore_error()):
                r_print(s.FAIL, type='fail')
                raise ProfileAddError({})
    
    if is_error_occured_in_current_scope:
        r_print(s.FAIL, type='fail')
    else:
        r_print(s.SUCCESS, type='success')
    
    

    ### Cleanup wlan profile xml files
    r_print(s.CLEANING_UP_TEMP, type='title')
    is_error_occured_in_current_scope = False

    for profile in WIFI_PROVISION_LIST:
        fname = f'{profile['name']}.xml'
        r_print(s.DELETING_NAME.format(fname), type='log', end='')
        
        try:
            fpath = os.path.join(XML_TARGET_DIR, fname)
            os.remove(fpath)
        
        except IOError as e:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(f' [red]{s.FAILED}[/red]', type='print')
            
            # Print shell output
            print_err_msg(e)
            
            # Ask user whether to continue or not
            if not(is_user_ignore_error()):
                r_print(s.FAIL, type='fail')
                raise IOError({'msg': e, 'on_event': 'CleanupTempFiles'})

        except Exception as e:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(f' [red]{s.FAILED}[/red]', type='print')
            
            # Print shell output
            print_err_msg(e)
            
            # Ask user whether to continue or not
            if not(is_user_ignore_error()):
                r_print(s.FAIL, type='fail')
                raise Exception({'msg': e, 'on_event': 'CleanupTempFiles'})
        
        else:
            r_print(f' [green]{s.DONE}[/green]', type='print')

    if is_error_occured_in_current_scope:
        r_print(s.FAIL, type='fail')
    else:
        r_print(s.SUCCESS, type='success')
    
    return is_error_occured



def main_wrapper():
    is_main_error = False
    return_code = 0

    try:
        is_main_error = main()
        
    except UnsupportedPlatformError as e:
        return_code = 2
        print_exception_msg(s.UNSUPPORTED_PLATFORM_TITLE,
                            s.UNSUPPORTED_PLATFORM_DESC.format('\"[bold underline bright_cyan]https://yis.yonsei.ac.kr/ics/service/internet.do[/bold underline bright_cyan]\"'))

    except UnsupportedVersionError as e:
        return_code = 2
        print_exception_msg(s.UNSUPPORTED_WINDOWS_VER_TITLE,
                            s.UNSUPPORTED_WINDOWS_VER_DESC.format('\"[bold underline bright_cyan]https://yis.yonsei.ac.kr/ics/service/internet.do[/bold underline bright_cyan]\"'))

    except WirelessInterfaceError as e:
        return_code = 2
        print_exception_msg(s.WLAN_IFACE_ERR_TITLE,
                            s.WLAN_IFACE_ERR_DESC)

    except WirelessServiceError as e:
        return_code = 2
        print_exception_msg(s.WLAN_SERVICE_ERR_TITLE,
                            s.WLAN_SERVICE_ERR_DESC)

    except InterfaceResetError as e:
        return_code = 2
        print_exception_msg(s.WLAN_SERVICE_ERR_TITLE,
                            s.IFACE_RESET_ERR_DESC)

    except ProfileDeletionError as e:
        return_code = 2
        print_exception_msg(s.DELETE_PROFILE_ERR_TITLE,
                            s.DELETE_PROFILE_ERR_DESC)

    except ProfileAddError as e:
        return_code = 2
        print_exception_msg(s.ADD_PROFILE_ERR_TITLE,
                            s.ADD_PROFILE_ERR_DESC)
    
    except IOError as e:
        return_code = 2

        if (type(e) == dict): # If we passed the exception with custom details
            if (e['on_event'] == 'GenerateProfile'):
                print_exception_msg(s.GEN_PROFILE_IOERR_TITLE,
                                    s.GEN_PROFILE_IOERR_DESC)

            elif (e['on_event'] == 'CleanupTempFiles'):
                print_exception_msg(s.CLEAN_TEMP_IOERR_TITLE,
                                    s.CLEAN_TEMP_IOERR_DESC)

        else: # Unexpected exceptions
            print_exception_msg(f'{s.UNEXPECTED_IOERR_TITLE}\n{str(e)}',
                                s.UNEXPECTED_IOERR_DESC)

    except Exception as e:
        return_code = 2

        if (type(e) == dict): # If we passed the exception with custom details
            if (e['on_event'] == 'GenerateProfile'):
                print_exception_msg(s.GEN_PROFILE_ERR_TITLE,
                                    s.GEN_PROFILE_ERR_DESC)

            elif (e['on_event'] == 'CleanupTempFiles'):
                print_exception_msg(s.CLEAN_TEMP_IOERR_TITLE,
                                    s.CLEAN_TEMP_IOERR_DESC)

        else: # Unexpected exceptions
            print_exception_msg(f'{s.UNEXPECTED_ERR_TITLE}\n{str(e)}',
                                s.UNEXPECTED_ERR_DESC)
    
    else: # Without any exceptions
        r_print('='*82 + '\n')
        
        text_completed = str(Figlet(font='nancyj').renderText(' Completed'))
        r_print(f'[bold bright_blue]{text_completed}[/bold bright_blue]\n')
        
        if (is_main_error): # Had some sort of error(s)
            return_code = 1
            r_print(f'[bold bright_red]{s.ONE_OR_MORE_ERROR}[/bold bright_red]')
            r_print(f'{s.YOU_MAY_NOT_ABLE_CONNECT}\n')
        
        else:# Without any errors. Hooray!
            r_print(f'{s.INSTALLATION_SUCCESSFUL}\n')
        
        r_print(s.NEXT_STEPS)
        r_print(f'  {s.NEXT_STEP_1}')
        r_print(f'  {s.NEXT_STEP_2}')
        r_print(f'  {s.NEXT_STEP_3}')
        r_print(f'     ({s.NEXT_STEP_3_DESC})')
        r_print(f'  {s.NEXT_STEP_4}\n')
        
        r_print(f'{s.IF_PROBLEM_CONTINUES}\n')
    
    r_print(s.PRESS_ANY_KEYS_EXIT, end='')
    pause_for_keys()
    r_print('')
    
    return return_code

if __name__ == '__main__':
    return_code = main_wrapper()
    exit(return_code)
else:
    raise Exception('Not a proper way to launch this app. Launch as standalone app.')