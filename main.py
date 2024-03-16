#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import string
import time
import ctypes
import locale
import gettext
from rich.console import Console

from platform_info import get_kernel_version, get_build_number, get_windows_version
from netsh_wrapper import Netsh
from error import *


APP_NAME = 'Yonsei Wi-Fi Security Profile Installer'
PACKAGE_NAME = 'Yonsei-WiFi-Profile-Installer'
APP_VER = '1.1 BETA'
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
IS_DEBUG = False
XML_TARGET_DIR = '.\\'
try:
    XML_TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys
    XML_TARGET_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    
TEXT_YONSEI = """         oooooo   oooo                                           o8o  
          `888.   .8'                                            `"'  
           `888. .8'    .ooooo.  ooo. .oo.    .oooo.o  .ooooo.  oooo  
            `888.8'    d88' `88b `888P"Y88b  d88(  "8 d88' `88b `888  
             `888'     888   888  888   888  `"Y88b.  888ooo888  888  
              888      888   888  888   888  o.  )88b 888    .o  888  
             o888o     `Y8bod8P' o888o o888o 8""888P' `Y8bod8P' o888o 
                                                                      
                                                                      """
TEXT_WIFI = """            oooooo   oooooo     oooo  o8o          oooooooooooo  o8o  
             `888.    `888.     .8'   `"'          `888'     `8  `"'  
              `888.   .8888.   .8'   oooo           888         oooo  
               `888  .8'`888. .8'    `888           888oooo8    `888  
                `888.8'  `888.8'      888  8888888  888    "     888  
                 `888'    `888'       888           888          888  
                  `8'      `8'       o888o         o888o        o888o 
                                                                      
                                                                      """
TEXT_COMPLETED = """    a88888b.                              dP            dP                  dP 
   d8'   `88                              88            88                  88 
   88        .d8888b. 88d8b.d8b. 88d888b. 88 .d8888b. d8888P .d8888b. .d888b88 
   88        88'  `88 88'`88'`88 88'  `88 88 88ooood8   88   88ooood8 88'  `88 
   Y8.   .88 88.  .88 88  88  88 88.  .88 88 88.  ...   88   88.  ... 88.  .88 
    Y88888P' `88888P' dP  dP  dP 88Y888P' dP `88888P'   dP   `88888P' `88888P8 
                                 88                                            
                                 dP                                            """


### Script-wide init

# Get current bundle dir (if inside pyinstaller) (https://stackoverflow.com/questions/61718298)
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
locale_dir = os.path.abspath(os.path.join(bundle_dir, 'locale'))

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

# Load translation
locale_code = ''

if os.name == 'nt':
    windll = ctypes.windll.kernel32
    locale_id = windll.GetUserDefaultUILanguage()
    locale_code = locale.windows_locale[locale_id]
else:
    env_lang = os.getenv('LANG')
    locale_code = env_lang.split('.')[0]
    
lang_code = 'en'

try:
    lang_code = locale_code.split('_')[0]
except:
    lang_code = 'en'

t=gettext.translation('main', locale_dir, languages=['ko'])
_ = t.gettext


# Set terminal title
if os.name == 'nt': # If OS is Windows
    ctypes.windll.kernel32.SetConsoleTitleW(APP_NAME)
# Load netsh wrapper module
netsh = Netsh(netsh_path=NETSH_PATH,
                xml_target_dir=XML_TARGET_DIR,
                wifi_profile_template=WIFI_PROFILE_TEMPLATE)


### Rich_Print
def r_print(msg: str, type: str = '', end='\n'):
    if (type == 'title'):
        console.print('*** {}'.format(msg), end=end)
    elif (type == 'log'):
        console.print('[bright_black]  - {}[/bright_black]'.format(msg), end=end)
    elif (type == 'log_bright'):
        console.print('  - {}'.format(msg), end=end)
    elif (type == 'success'):
        console.print('  [bold bright_green]{} {}[/bold bright_green]\n\n'.format(check_mark, msg), end=end)
    elif (type == 'fail'):
        console.print('  [bold bright_red]{} {}[/bold bright_red]\n\n'.format(cross_mark, msg), end=end)
    else:
        console.print(msg, end=end)
    return


def is_user_ignore_error():
    r_print(_('One or more error has occurred') + '. ' + _('This may cause additional errors.'))
    
    user_input = ''
    while True:
        user_input = input(_('Do you want to ignore this error and continue?') + ' [Y/n]: ')
        
        if (user_input.lower() == 'y'):
            r_print(_('Continuing the installation...'), type='log')
            return True

        elif (user_input.lower() == 'n'):
            r_print(_('Exiting the installation...'), type='log')
            return False

        else:
            r_print(_('\"{}\" is not a valid input.').format(user_input) + '\n')
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
    new_msg = _('[None]') + '\n' if (new_msg == '') else new_msg
    
    # Print message
    r_print('')
    r_print(_('Error message:'))
    r_print(new_msg)


def print_exception_msg(msg:str = '', desc:str = ''):
    # Prefix
    r_print('='*82 + '\n')
    r_print('[bright_red]{}[/bright_red]\n'.format(_('Installation Failed.')))
    r_print('{}:\n'.format(_('One or more error has occurred')))
    
    # Main msg
    r_print('[bold bright_white]{}[bold bright_white]\n'.format(msg))
    
    # Desc
    r_print(desc + '\n')
    
    # Suffix
    r_print(_('The installer cannot continue.'))
    r_print(_('If a problem occurs or cannot connect to Wi-Fi, contact school IT department for assistance.'))
    
    return


def main():
    ### Init main func
    is_error_occured = False
    is_error_occured_in_current_scope = False
        
    ### Print intro
    text_app_info = f'{APP_NAME} (Version: {APP_VER}) by {APP_AUTHOR}'
    
    r_print('')
    r_print('[bold bright_blue]' + TEXT_YONSEI + '[/bold bright_blue]')
    r_print('[bold bright_white]' + TEXT_WIFI + '[/bold bright_white]')
    r_print(' '*6 + '[bright_black]' + text_app_info + '[/bright_black]')
    
    r_print('='*82 + '\n')
    
    r_print(_('This installer will install Yonsei Wi-Fi Security profiles to enable\nthe connection of fast and secure Yonsei Wi-Fi on your Windows device.') + '\n')
    
    r_print(_('Close all applications and refrain from using the device to prevent possible collision.'))
    r_print(_('The installer will begin installing Wi-Fi Security profiles in 5 seconds...'))
    
    time.sleep(5)
    
    r_print('')
    r_print(_('Starting installation...'))
    r_print('')
    
    time.sleep(2)
    
    r_print('-'*82 + '\n\n')
    

    ### Check system version
    r_print(_('Checking system requirements...'), type='title')
    
    r_print(_('Detected Platform: {}').format(platform.system()), type='log')
    
    if (platform.system().lower() != 'windows'):
        r_print(_('Detected OS: {}').format(platform.platform()), type='log')
        r_print(_('Unsupported platform.'), type='log')
        r_print(_('Fail'), type='fail')
        raise UnsupportedPlatformError({'platform_info': platform.platform()})
    
    kernel_ver = get_kernel_version()
    build_num = get_build_number()
    windows_ver = get_windows_version()
    
    r_print(_('Detected OS: {} (Build {})').format(windows_ver, build_num), type='log')
    
    if (float(kernel_ver) < MINIMUM_KERNEL_VER):
        r_print(_('Windows version too low.'), type='log')
        r_print(_('Fail'), type='fail')
        raise UnsupportedVersionError({'platform_info': windows_ver})
    else:
        r_print(_('Success'), type='success')
    
    

    ### Check interface state
    r_print(_('Checking wireless interface...'), type='title')
    
    wlan_result = netsh.get_wlan_interface_state()
    r_print(_('Interface state: {}').format(wlan_result['state']), type='log')
    
    if (wlan_result['state'] == 'ERR_SERVICE'):
        r_print(_('Service \"WLAN AutoConfig\" (wlansvc) is not running.'), type='log')
        r_print(_('Fail'), type='fail')
        raise WirelessServiceError({})
    
    elif (wlan_result['state'] == 'ERR_INTERFACE'):
        r_print(_('Wireless interface not found.'), type='log')
        r_print(_('Fail'), type='fail')
        raise WirelessInterfaceError({})
    
    r_print(_('Wireless interface is normal.'), type='log')
    r_print(_('Success'), type='success')
    


    ### Initialize wireless interface
    r_print(_('Preparing wireless interface...'), type='title')
    r_print(_('Disconnecting Wi-Fi...'), type='log', end='')
    
    result_disconnect = netsh.disconnect()
    
    if (result_disconnect.returncode == 0):
        r_print(' [green]{}[/green]'.format(_('done')))
        r_print(_('Success'), type='success')

    else:
        r_print(' [red]{}[/red]'.format(_('failed')))
        r_print(_('Fail'), type='fail')
        
        # Print shell output
        print_err_msg(result_disconnect.stdout + result_disconnect.stderr)
        
        # Ask user whether to continue or not
        if not(is_user_ignore_error()):
            raise InterfaceResetError({})
        
        is_error_occured = True
    
    

    ### Delete old wlan profiles
    r_print(_('Deleting old Wi-Fi profiles...'), type='title')
    is_error_occured_in_current_scope = False
    
    for profile_name in WIFI_PROFILE_DELETE_TARGETS:
        r_print(_('Deleting profile \"{}\"...').format(profile_name), type='log', end='')
        
        result_del_profile = netsh.del_profile(profile_name=profile_name)
        
        if (result_del_profile.returncode == 0):
            r_print(' [green]{}[/green]'.format(_('done')), type='print')

        else:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(' [red]{}[/red]'.format(_('failed')), type='print')
            
            print_err_msg(result_del_profile.stdout + result_del_profile.stderr)
            
            if not(is_user_ignore_error()):
                r_print(_('Fail'), type='fail')
                raise ProfileDeletionError({})
    
    if is_error_occured_in_current_scope:
        r_print(_('Fail'), type='fail')
    else:
        r_print(_('Success'), type='success')
    
    

    ### Generate wlan profile xml files
    r_print(_('Generating new Wi-Fi profiles...'), type='title')
    
    for profile in WIFI_PROVISION_LIST:
        r_print(_('Generating profile \"{}\"...').format(profile['name']), type='log', end='')
        
        try:
            netsh.generate_profile_xml(name=profile['name'], hex=profile['hex'], server_name=profile['server_name'])
            
        except IOError as e:
            r_print(' [red]{}[/red]'.format(_('failed')), type='print')
            r_print(_('Fail'), type='fail')
            raise IOError({'msg': e, 'on_event': 'GenerateProfile'})

        except Exception as e:
            r_print(' [red]{}[/red]'.format(_('failed')), type='print')
            r_print(_('Fail'), type='fail')
            raise Exception({'msg': e, 'on_event': 'GenerateProfile'})

        else:
            r_print(' [green]{}[/green]'.format(_('done')), type='print')
    
    r_print(_('Success'), type='success')
    
    

    ### Adding wlan profile xml files via netsh
    r_print(_('Adding new Wi-Fi profiles to system...'), type='title')
    is_error_occured_in_current_scope = False
    
    for profile in WIFI_PROVISION_LIST:
        r_print(_('Adding profile \"{}\" to system...').format(profile['name']), type='log', end='')
        
        fname = profile['name'] + '.xml'
        fpath = os.path.join(XML_TARGET_DIR, fname)
        result_add_profile = netsh.add_profile('\"' + fpath + '\"')
        
        if (result_add_profile.returncode == 0):
            r_print(' [green]{}[/green]'.format(_('done')), type='print')

        else:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(' [red]{}[/red]'.format(_('failed')), type='print')
            
            # Print shell output
            print_err_msg(result_add_profile.stdout + result_add_profile.stderr)
            
            # Ask user whether to continue or not
            if not(is_user_ignore_error()):
                r_print(_('Fail'), type='fail')
                raise ProfileAddError({})
    
    if is_error_occured_in_current_scope:
        r_print(_('Fail'), type='fail')
    else:
        r_print(_('Success'), type='success')
    
    

    ### Cleanup wlan profile xml files
    r_print(_('Cleaning up temporary files...'), type='title')
    is_error_occured_in_current_scope = False

    for profile in WIFI_PROVISION_LIST:
        fname = profile['name'] + '.xml'
        r_print(_('Deleting \"{}\"...').format(fname), type='log', end='')
        
        try:
            fpath = os.path.join(XML_TARGET_DIR, fname)
            os.remove(fpath)
        
        except IOError as e:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(' [red]{}[/red]'.format(_('failed')), type='print')
            
            # Print shell output
            print_err_msg(e)
            
            # Ask user whether to continue or not
            if not(is_user_ignore_error()):
                r_print(_('Fail'), type='fail')
                raise IOError({'msg': e, 'on_event': 'CleanupTempFiles'})

        except Exception as e:
            is_error_occured = True
            is_error_occured_in_current_scope = True
            r_print(' [red]{}[/red]'.format(_('failed')), type='print')
            
            # Print shell output
            print_err_msg(e)
            
            # Ask user whether to continue or not
            if not(is_user_ignore_error()):
                r_print(_('Fail'), type='fail')
                raise Exception({'msg': e, 'on_event': 'CleanupTempFiles'})
        
        else:
            r_print(' [green]{}[/green]'.format(_('done')), type='print')

    if is_error_occured_in_current_scope:
        r_print(_('Fail'), type='fail')
    else:
        r_print(_('Success'), type='success')
    
    return is_error_occured



def main_wrapper():
    is_main_error = False
    return_code = 0

    try:
        is_main_error = main()
        
    except UnsupportedPlatformError as e:
        return_code = 2
        print_exception_msg(_('Current machine\'s OS is not supported.'),
                            _('Visit {} and\nfind appropriate Wi-Fi connection guide for current device.').format('\"[bold underline bright_cyan]https://yis.yonsei.ac.kr/ics/service/internet.do[/bold underline bright_cyan]\"'))

    except UnsupportedVersionError as e:
        return_code = 2
        print_exception_msg(_('Current machine\'s Windows version is not supported.'),
                            _('Upgrade to newer versions of Windows or\nVisit {} and\nfind appropriate Wi-Fi connection guide for current Windows version.\n(Minimum supported version of Windows is Windows 8.)').format('\"[bold underline bright_cyan]https://yis.yonsei.ac.kr/ics/service/internet.do[/bold underline bright_cyan]\"'))

    except WirelessInterfaceError as e:
        return_code = 2
        print_exception_msg(_('Wireless interface (Wi-Fi Card) is not detected or\ncannot be accessed on your device.'),
                            _('This installer only works on Wi-Fi-capable devices.\nTry rebooting the device or updating/reinstalling the Wi-Fi driver.'))

    except WirelessServiceError as e:
        return_code = 2
        print_exception_msg(_('\"WLAN AutoConfig\" (wlansvc) service is not running on your device.'),
                            _('Try enabling and starting the required service, then run this installer.'))

    except InterfaceResetError as e:
        return_code = 2
        print_exception_msg(_('Failed to disconnect Wi-Fi before installing new profile.'),
                            _('Try running the installer again. If the problem persists,\ntry rebooting the device or updating/reinstalling Wi-Fi driver.'))

    except ProfileDeletionError as e:
        return_code = 2
        print_exception_msg(_('Failed to delete old Wi-Fi profile(s).'),
                            _('Try running the installer again. If the problem persists, try rebooting the device.'))

    except ProfileAddError as e:
        return_code = 2
        print_exception_msg(_('File write failed while generating new Wi-Fi profile file(s).'),
                            _('Try closing all opened applications or rebooting the device then run this installer.'))
    
    except IOError as e:
        return_code = 2

        if (type(e) == dict): # If we passed the exception with custom details
            if (e['on_event'] == 'GenerateProfile'):
                print_exception_msg(_('File write failed while generating new Wi-Fi profile file(s).'),
                                    _('Try closing all opened applications or rebooting the device then run this installer.'))

            elif (e['on_event'] == 'CleanupTempFiles'):
                print_exception_msg(_('Deleting temporary file(s) failed.'),
                                    _('Try closing all opened applications or rebooting the device then run this installer.'))

        else: # Unexpected exceptions
            print_exception_msg( _('Unexpected File IO error occurred:') + '\n' + str(e),
                                _('Try closing all opened applications or rebooting the device then run this installer.'))

    except Exception as e:
        return_code = 2

        if (type(e) == dict): # If we passed the exception with custom details
            if (e['on_event'] == 'GenerateProfile'):
                print_exception_msg(_('Generating new Wi-Fi profile file(s) failed.'),
                                    _('Try closing all opened applications or rebooting the device then run this installer.'))

            elif (e['on_event'] == 'CleanupTempFiles'):
                print_exception_msg(_('Deleting temporary file(s) failed.'),
                                    _('Try closing all opened applications or rebooting the device then run this installer.'))

        else: # Unexpected exceptions
            print_exception_msg(_('Unexpected Error occurred:') + '\n' + str(e),
                                _('Try closing all opened applications or rebooting the device then run this installer.'))
    
    else: # Without any exceptions
        r_print('='*82 + '\n')
        
        r_print('[bold bright_blue]{}[/bold bright_blue]\n'.format(TEXT_COMPLETED))
        
        if (is_main_error): # Had some sort of error(s)
            return_code = 1
            r_print('[bold bright_red]{}[/bold bright_red]'.format(_('One or more error has occurred')))
            r_print(_('You may not be able to connect to Yonsei Wi-Fi.') + '\n')
        
        else:# Without any errors. Hooray!
            r_print(_('Wi-Fi Profile installation was successful.') + '\n')
        
        r_print(_('Next steps:'))
        r_print('  ' + _('1. Open Wi-Fi menu from the settings app or the taskbar.'))
        r_print('  ' + _('2. Connect to one of Yonsei Wi-Fi networks (Yonsei, eduroam).'))
        r_print('  ' + _('3. Enter your Yonsei portal credential when asked.'))
        r_print('     (' + _('Username: Your student ID number, Password: Your portal password') + ')')
        r_print('  ' + _('4. Enjoy your secure Yonsei Wi-Fi!') + '\n')
        
        r_print(_('If a problem occurs or cannot connect to Wi-Fi, contact school IT department for assistance.') + '\n')
    
    if os.name == 'nt': # If OS is Windows
        r_print(_('Press any keys to exit...'), end='')
        os.system('pause >nul')
    else:
        r_print(_('Press Enter key to exit...'), end='')
        input()
    return
    r_print('')
    
    return return_code

if __name__ == '__main__':
    return_code = main_wrapper()
    exit(return_code)
else:
    raise Exception('Not a proper way to launch this app. Launch as standalone app.')