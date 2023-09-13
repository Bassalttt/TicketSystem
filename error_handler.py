'''
Index:
    AuthorizationException
    InputException
    TicketDBException
    ErrorTraceBack
'''
import sys
import traceback

from namespace import AuthorizeationError, TicketDBError

class AuthorizationException(Exception):
    '''Authorization exception.'''
    def __init__(self, error: AuthorizeationError):
        self.error_type = error

class InputException(Exception):
    '''Input exception.'''
    def __init__(self, error: TicketDBError) -> None:
        self.error_type = error

class TicketDBException(Exception):
    '''Ticket DB exception.'''
    def __init__(self, error: TicketDBError) -> None:
        self.error_type = error

class ErrorTraceBack():
    '''Error trace back.'''
    def __init__(self) -> None:
        pass

    def error_msg(self, error_title: str = '') -> None:
        '''Show error message.'''
        _, error_value, exc_traceback = sys.exc_info() # get Call Stack
        last_call_stack = traceback.extract_tb(exc_traceback) [-1] # get the last call back
        file_name = last_call_stack [0]
        line_num = last_call_stack[1]
        func_name = last_call_stack[2]
        print(f'\n{error_title}:{error_value}')
        print('\tLocate at')
        print(f'\t\tFile: {file_name}')
        print(f'\t\tFunc: {func_name}()')
        print(f'\tLine:\t{line_num}')
