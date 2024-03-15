#!/usr/local/bin/python
# -*- coding: utf-8 -*-

def error_msg_handler(msg: str = '', output: str = None):
    pass

class UnsupportedPlatformError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return
    

class UnsupportedVersionError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return


class WirelessInterfaceError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return


class WirelessServiceError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return


class InterfaceResetError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return


class ProfileDeletionError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return


class ProfileAddError(Exception):
    def __init__(self, message='', errors=''):
        self.message = message
        self.errors = errors
        super().__init__(self.message)

        # Custom code
        
        return
