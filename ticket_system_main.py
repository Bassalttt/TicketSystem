'''
Index:
    TicketSystem
'''
from crud import CrudHandler
from error_handler import AuthorizationException, InputException, TicketDBException
from error_handler import ErrorTraceBack
from namespace import UserIdentity, InputError
import ticket_db
from ticket_db import NormalGetSheetColumn, ParseTicketDB, WriteDB
from user import UserPM, UserQA, UserRD

TICKET_FILE = r'\THE\PATH\ticket.xlsx'

class TicketSystem():
    '''Ticket system'''
    def __init__(self) -> None:
        self.__all_ticket = [] # [TicketFormat] self.current_user = None # User obj
        self.crud_adapter = None # CrudAdpater obj

    def __get_all_ticket(self, ticket_path) -> None:
        '''Get all the ticket in the sheet.'''
        sheet_column_interface = NormalGetSheetColumn()
        self.__all_ticket = ParseTicketDB(ticket_path, sheet_column_interface).get_content()

    def __load_user_information(self, name:str, identity:str) -> None:
        '''Load user identity.'''
        if identity == UserIdentity.PM.value:
            self.current_user = UserPM(name)
        elif identity == UserIdentity.QA.value:
            self.current_user = UserQA(name)
        elif identity == UserIdentity.RD.value:
            self.current_user = UserRD(name)
        else:
            raise InputException(InputError.NoSuchIdentity)

    def __save_ticket(self) -> None:
        '''Save all tickets to the sheet.'''
        WriteDB(self.__all_ticket).fill_in(TICKET_FILE)
        print("File saved.")

    def __preprocess(self) -> None:
        '''Get name and identity.'''
        self.__get_all_ticket(TICKET_FILE)
        name = input("Enter your name: ")
        identity = input("Enter your identity (PM/QA/RD): ").upper()
        print("Loading user information.")
        self.__load_user_information(name, identity)
        self.crud_adapter = CrudHandler(self.current_user, self.__all_ticket)

    def __operate(self):
        '''Let the user decide what he/she want to do.'''
        user_auth= self.current_user.get_authorization()
        action = input("What do you want to do? %s: " % user_auth).upper()
        self.crud_adapter.choose_crud (action)

    def run_system(self):
        '''Go!'''
        try:
            self.__preprocess()
            self.__operate()
            self.__save_ticket()

        except TicketDBException:
            error_title = "DB error"
            ErrorTraceBack().error_msg(error_title)

        except InputException:
            error_title = "Wrong input"
            ErrorTraceBack().error_msg(error_title)
 
        except AuthorizationException:
            error_title = "Authorization error"
            ErrorTraceBack().error_msg(error_title)

        except Exception:
            error_title = "Unknown Error"
            ErrorTraceBack().error_msg(error_title)

if __name__ == '__main__':
    ticket_db.TICKET_FILE = TICKET_FILE
    TicketSystem().run_system()
