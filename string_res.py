#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import locale
import ctypes
import gettext

locale_code = ''

if os.name == 'nt':
    windll = ctypes.windll.kernel32
    locale_id = windll.GetUserDefaultUILanguage()
    locale_code = locale.windows_locale[locale_id]
else:
    env_lang = os.getenv('LANG')
    locale_code = env_lang.split('.')[0]

t=gettext.translation('string_res', 'locale', languages=[locale_code], fallback=True)
_ = t.gettext


class StringRsc:
    def __init__(self) -> None:
        pass
    
    def get_string(id:str):
        return
    
    # Common
    NONE = _('[None]')
    FAIL = _('Fail')
    FAILED = _('failed')
    SUCCESS = _('Success')
    DONE = _('done')
    ONE_OR_MORE_ERROR = _('One or more error has occurred.')
    IF_PROBLEM_CONTINUES = _('If a problem occurs or cannot connect to Wi-Fi, contact school IT department for assistance.')
    PRESS_ANY_KEYS_EXIT = _('Press any keys to exit...')
    
    THIS_MAY_CAUSE_ADDITIONAL = _('This may cause additional errors.')
    IGNORE_AND_CONTINUE = _('Do you want to ignore this error and continue?')
    CONTINUING_INSTALL = _('Continuing the installation...')
    EXITING_INSTALL = _('Exiting the installation...')
    IS_NOT_VALID_INPUT = _('\"{}\" is not a valid input.')
    ERROR_MESSAGE = _('Error message:')
    
    # def print_exception_msg:
    INSTALLATION_FAILED = _('Installation Failed.')
    CANNOT_CONTINUE = _('The installer cannot continue.')
    
    ### Print intro
    CLOSE_ALL_APPS_AND_REFRAIN = _('Close all applications and refrain from using the device to prevent possible collision.')
    WILL_BEGIN_IN_FIVE = _('The installer will begin installing Secure Wi-Fi profiles in 5 seconds...')
    STARTING_INSTALL = _('Starting installation...')
    
    ### Check system version
    CHECKING_SYS_REQ = _('Checking system requirements...')
    DETECTED_OS = _('Detected OS: {} (Build {})')
    DETECTED_OS_OTHER = _('Detected OS: {}')
    UNSUPPORTED_PLATFORM = _('Unsupported platform.')
    WIN_VER_TOO_LOW = _('Windows version too low.')
    
    ### Check interface state
    CHECKING_WLAN_IFACE = _('Checking wireless interface...')
    INTERFACE_STATE = _('Interface state: {}')
    SVC_NOT_RUNNING = _('Service \"WLAN AutoConfig\" (wlansvc) is not running.')
    WLAN_IFACE_NOTFOUND = _('Wireless interface not found.')
    WLAN_IFACE_NORMAL = _('Wireless interface is normal.')
    
    ### Initialize wireless interface
    PREPARING_WLAN_IFACE = _('Preparing wireless interface...')
    DISCONNECTING_WIFI = _('Disconnecting Wi-Fi...')
    
    ### Delete old wlan profiles
    DELETING_OLD_PROFILES = _('Deleting old Wi-Fi profiles...')
    DELETING_PROFILE_NAME = _('Deleting profile \"{}\"...')
    
    ### Generate wlan profile xml files
    GENERATING_NEW_PROFILES = _('Generating new Wi-Fi profiles...')
    GENERATING_PROFILE_NAME = _('Generating profile \"{}\"...')
    
    ### Adding wlan profile xml files via netsh
    ADDING_NEW_PROFILES = _('Adding new Wi-Fi profiles to system...')
    ADDING_PROFILE_NAME = _('Adding profile \"{}\" to system...')
    
    ### Cleanup wlan profile xml files
    CLEANING_UP_TEMP = _('Cleaning up temporary files...')
    DELETING_NAME = _('Deleting \"{}\"...')
    
    ### Result screen
    YOU_MAY_NOT_ABLE_CONNECT = _('You may not be able to connect to Yonsei Wi-Fi.')
    INSTALLATION_SUCCESSFUL = _('Wi-Fi Profile installation was successful.')
    NEXT_STEPS = _('Next steps:')
    NEXT_STEP_1 = _('1. Open Wi-Fi menu from the settings app or the taskbar.')
    NEXT_STEP_2 = _('2. Connect to one of Yonsei Wi-Fi networks (Yonsei, eduroam).')
    NEXT_STEP_3 = _('3. Enter your Yonsei portal credential when asked.')
    NEXT_STEP_3_DESC = _('Username: Your student ID number, Password: Your portal password')
    NEXT_STEP_4 = _('4. Enjoy your secure Yonsei Wi-Fi!')
    
    ### ERROR_MSG
    UNSUPPORTED_PLATFORM_TITLE = _('Current machine\'s OS is not supported.')
    UNSUPPORTED_PLATFORM_DESC = _('Visit {} and\nfind appropriate Wi-Fi connection guide for current device.')
    
    UNSUPPORTED_WINDOWS_VER_TITLE = _('Current machine\'s Windows version is not supported.')
    UNSUPPORTED_WINDOWS_VER_DESC = _('Upgrade to newer versions of Windows or\nVisit {} and\nfind appropriate Wi-Fi connection guide for current Windows version.\n(Minimum supported version of Windows is Windows 8.)')
    
    WLAN_IFACE_ERR_TITLE = _('Wireless interface (Wi-Fi Card) is not detected or\ncannot be accessed on your device.')
    WLAN_IFACE_ERR_DESC = _('This installer only works on Wi-Fi-capable devices.\nTry rebooting the device or updating/reinstalling the Wi-Fi driver.')
    
    WLAN_SERVICE_ERR_TITLE = _('\"WLAN AutoConfig\" (wlansvc) service is not running on your device.')
    WLAN_SERVICE_ERR_DESC = _('Try enabling and starting the required service, then run this installer.')
    
    IFACE_RESET_ERR_TITLE = _('Failed to disconnect Wi-Fi before installing new profile.')
    IFACE_RESET_ERR_DESC = _('Try running the installer again. If the problem persists,\ntry rebooting the device or updating/reinstalling Wi-Fi driver.')
    
    DELETE_PROFILE_ERR_TITLE = _('Failed to delete old Wi-Fi profile(s).')
    DELETE_PROFILE_ERR_DESC = _('Try running the installer again. If the problem persists, try rebooting the device.')
    
    ADD_PROFILE_ERR_TITLE = _('Failed to add new Wi-Fi profile(s).')
    ADD_PROFILE_ERR_DESC = _('Try running the installer again. If the problem persists, try rebooting the device.')
    
    GEN_PROFILE_IOERR_TITLE = _('File write failed while generating new Wi-Fi profile file(s).')
    GEN_PROFILE_IOERR_DESC = _('Try closing all opened applications or rebooting the device then run this installer.')
    
    GEN_PROFILE_ERR_TITLE = _('Generating new Wi-Fi profile file(s) failed.')
    GEN_PROFILE_ERR_DESC = _('Try closing all opened applications or rebooting the device then run this installer.')
    
    CLEAN_TEMP_IOERR_TITLE = _('Deleting temporary file(s) failed.')
    CLEAN_TEMP_IOERR_DESC = _('Try closing all opened applications or rebooting the device then run this installer.')
    
    CLEAN_TEMP_IOERR_TITLE = _('Deleting temporary file(s) failed.')
    CLEAN_TEMP_IOERR_DESC = _('Try closing all opened applications or rebooting the device then run this installer.')
    
    UNEXPECTED_IOERR_TITLE = _('Unexpected File IO error occurred:')
    UNEXPECTED_IOERR_DESC = _('Try closing all opened applications or rebooting the device then run this installer.')
    
    UNEXPECTED_ERR_TITLE = _('Unexpected Error occurred:')
    UNEXPECTED_ERR_DESC = _('Try closing all opened applications or rebooting the device then run this installer.')