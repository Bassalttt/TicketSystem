'''
Index:
    CrudHandler
    TicketCreater
    TicketReader
    TicketUpdater
    TicketDeleter
    TicketAccessChecker
    TicketExistChecker
    EmilSender
'''

from copy import deepcopy
from typing import List

# import win32com.client as win32

from error_handler import AuthorizationException, InputException
from namespace import TicketStatus, TicketType
from namespace import Authorization, AuthorizeationError, InputError
from ticket_db import TicketFormat
from user import UserInterface

class CrudHandler():
    '''Handle create, read, update, and delete.'''
    def __init__(self, user: UserInterface, all_ticket: List[TicketFormat]) -> None:
        self.__user = user
        self.__all_ticket = all_ticket

    def choose_crud(self, action: str) -> None:
        '''Choose and execute the funciton.'''
        if action == Authorization.Create.value:
            if self.__user.is_creatable:
                self.__create_ticket()
            else:
                raise AuthorizationException(AuthorizeationError.NoAuthorization)

        elif action == Authorization.Read.value:
            if self.__user.is_readable:
                self.__read_ticket()
            else:
                raise AuthorizationException(AuthorizeationError.NoAuthorization)

        elif action == Authorization.Update.value:
            if self.__user.is_updatable:
                self.__update_ticket()
            else:
                raise AuthorizationException(AuthorizeationError.NoAuthorization)

        elif action == Authorization.Delete.value:
            if self.__user.is_deletable:
                self.__delete_ticket()
            else:
                raise AuthorizationException(AuthorizeationError.NoAuthorization)

        else:
            raise InputException(InputError.NoSuchOperation)

        return self.__all_ticket

    def __create_ticket(self) -> None:
        '''Create a ticket.'''
        new_ticket = TicketCreater(self.__user.name, self.__user.create_condition).create()
        self.__all_ticket.append(new_ticket)

    def __read_ticket(self) -> None:
        '''Read a ticket.'''
        read_cond = self.__user.read_condition
        TicketReader(read_cond, self.__all_ticket).read()

    def __update_ticket(self) -> None:
        '''Update a ticket.'''
        read_cond = self.__user.read_condition
        update_cont = self.__user.update_content
        TicketUpdater(read_cond, update_cont, self.__all_ticket).update_ticket()
        #self._read_ticket()

    def __delete_ticket(self) -> None:
        '''Delete a ticket.'''
        TicketDeleter(self.__all_ticket).delete_ticket()
        # self._read_ticket()

class TicketCreater():
    '''Create a ticket.'''
    def __init__(self, user_name: str, create_condition: TicketFormat) -> None:
        self.__user_name = user_name
        self.__email_sender = EmilSender()
        self.__create_condition = create_condition

    def __choose_ticket_type(self) -> str:
        '''Choose ticket type, Bug or NewFeature, when creating.'''
        type_create_cond = self.__create_condition.ticket_type
        if type_create_cond != False:
            options = ['1.'+type_create_cond.value]
        else:
            options = [str(i+1)+'.'+a.name for i, a in enumerate(TicketType)]

        if len(options) == 1:
            number = 0
        else:
            number = int(input('Type: %s:' % (options)))

        try:
            choice = options[number-1].split('.')[1]
        except:
            raise InputException(InputError.NoSuchOption)
        return choice

    def create(self) -> TicketFormat:
        '''Create a ticket.'''
        title = input('Title: ')
        description = input('Description: ')
        assign_to = input('Assign_to: ')
        status = TicketStatus.Waiting.value
        ticket_type = self.__choose_ticket_type()
        create_ticket = TicketFormat(title,
                                    description,
                                    assign_to,
                                    status,
                                    self.__user_name,
                                    ticket_type)
        create_msg = '%s has been created.' % title
        print(create_msg)
        self.__email_sender.send(assign_to, create_msg)
        return create_ticket

class TicketReader():
    '''Read tickets.'''
    def __init__(self,
                read_condition: TicketFormat,
                all_ticket: TicketFormat) -> None:
        self.__read_condition = read_condition
        self.__all_ticket = all_ticket

    def read(self) -> None:
        '''Read all ticket'''
        for ticket in self.__all_ticket:
            if TicketAccessChecker(self.__read_condition).check_accessible(ticket):
                print('Title: %s' % ticket.title)
                print('\tDescription: %s' % ticket.description)
                print('\tAssign to: %s' % ticket.assign_to)
                print('\tStatus: %s' % ticket.status)
                print('\tSubmitter: %s' % ticket.submitter)
                print('\tType: %s' % ticket.ticket_type)
                print('')

class TicketUpdater():
    '''Update a ticket.'''
    def __init__(self,
                read_condition: TicketFormat,
                update_content: TicketFormat,
                all_ticket: List[TicketFormat])-> None:
        self.__read_condition = read_condition
        self.__update_content = update_content
        self.__all_ticket = all_ticket
        self.__email_sender = EmilSender()

    def __get_dscptn(self) -> bool:
        '''Get description info.'''
        return self.__update_content.description

    def __get_assign_to(self) -> bool:
        '''Get assign_to info.'''
        return self.__update_content.assign_to

    def __get_status(self) -> bool or TicketStatus:
        '''Get status info.'''
        return self.__update_content.status

    def __get_submtr(self) -> bool:
        '''Get submitter info.'''
        return self.__update_content.submitter

    def __get_tkt_type(self) -> bool:
        '''Get ticket type info.'''
        return self.__update_content.ticket_type

    def __update(self, updateable:bool or str, update_item:str, ori_content:str) -> str:
        '''Update update_item.'''
        if updateable == True:
            change = input('Change %s? (Y/N): ' % update_item).upper()
            if change == 'Y':
                return input('\tUpdate %s:' % update_item)
            else:
                return ori_content
        elif updateable == False:
            return ori_content
        else:
            return updateable

    def __multiple_choice(self,
                        updateable: bool,
                        update_item: str,
                        ori_content: str,
                        obj: object) -> str:
        '''Multiple choice for some field.'''
        if updateable == True:
            change = input('Change %s? (Y/N): ' % update_item).upper()
            if change == 'Y':
                options = [str(i+1)+'.'+a.name for i, a in enumerate(obj)]
                number = int(input('\tUpdate %s:%s' % (update_item, options)))
                try:
                    choice = [a.name for i, a in enumerate(obj) if i+1 == number][0]
                except:
                    raise InputException(InputError.NoSuchOption)
            else:
                choice = ori_content
        else:
            choice = ori_content
        return choice

    def __inform_creater(self, ticket: TicketFormat, update_msg: str) -> None:
        '''Information creater.'''
        if ticket.status == TicketStatus.Done.value:
            self.__email_sender.send(ticket.submitter, update_msg)

    def update_ticket(self) -> None:
        '''Update a ticket according to the ticket name.'''
        ticket_title = input('Enter a ticket name: ')
        all_ticket = deepcopy(self.__all_ticket)
        access_checker = TicketAccessChecker(self.__read_condition)
        ticket_exist = False

        for i, ticket in enumerate(all_ticket):
            accessible = access_checker.check_accessible(ticket)
            if ticket_title == ticket.title and accessible:
                ticket.description = self.__update(self.__get_dscptn(),
                                                   'description',
                                                   ticket.description)
                ticket.assign_to = self.__update(self.__get_assign_to(),
                                                 'assign_to',
                                                 ticket.assign_to)
                ticket.status = self.__multiple_choice(self.__get_status(),
                                                       'status',
                                                       ticket.status,
                                                       TicketStatus)
                ticket.submitter = self.__update(self.__get_submtr(),
                                                 'submitter',
                                                 ticket.submitter)
                ticket.ticket_type = self.__multiple_choice(self.__get_tkt_type(),
                                                            'ticket_type',
                                                            ticket.ticket_type, TicketType)
                self.__all_ticket[i] = ticket
                update_msg = '%s has been updated.' % ticket_title
                print(update_msg)
                self.__inform_creater(ticket, update_msg)
                ticket_exist = True
                break
        TicketExistChecker.check_exist(ticket_exist)

class TicketDeleter():
    '''Delete a ticket.'''
    def __init__(self, all_ticket: List[TicketFormat]) -> None:
        self.__all_ticket = all_ticket

    def delete_ticket(self) -> None:
        '''Delete.'''
        ticket_title = input('Enter a ticket name: ')
        all_ticket = deepcopy(self.__all_ticket)
        ticket_exist = False

        for i, ticket in enumerate(all_ticket):
            if ticket.title == ticket_title:
                print('%s has been deleted.' % ticket_title)
                del self.__all_ticket[i]
                ticket_exist = True
                break
        TicketExistChecker.check_exist(ticket_exist)

class TicketAccessChecker():
    '''Check ticket accessible for different identity.'''
    def __init__(self, condition: TicketFormat) -> None:
        self.__condition = condition

    def __check_condition(self, condition: bool, item: str):
        '''Check condition.'''
        if condition != False and condition != item:
            raise False
        else:
            pass

    def check_accessible(self, one_ticket: TicketFormat) -> bool:
        '''Check accessible.'''
        try:
            assignto_cond = self.__condition.assign_to
            self.__check_condition(assignto_cond, one_ticket.assign_to)

            status_cond = self.__condition.status
            self.__check_condition(status_cond, one_ticket.status)

            sm_cond = self.__condition.submitter
            self.__check_condition(sm_cond, one_ticket.submitter)

            ttype_cond = self.__condition.ticket_type
            self.__check_condition(ttype_cond, one_ticket.ticket_type)
            return True
        except:
            return False

class TicketExistChecker():
    '''Check if the ticket exist.'''
    def check_exist(checker: bool) -> None:
        '''Check.'''
        if checker:
            return
        else:
            raise InputException(InputError.NoSuchOption)

class EmilSender():
    '''Send E-mail.'''
    # def __init__(self, send_to:str, send_msg:str) -> None:
    #   self.send_to = send_to
    #   self.send_msg = send_msg

    def send(self, send_to: str, send_msg: str) -> None:
        '''Send.'''
        receiver = send_to + '@XXXXXXX.com'
        confirm_sending = input(f'Send the mail to {receiver}? (Y/N):').upper()
        if confirm_sending == 'Y':
            # outlook = win32.Dispatch('outlook.application')
            # mail = outlook.CreateItem(0)
            # mail.To = receiver
            # mail.Subject = send_msg
            # mail.body = send_msg
            # mail.Send()
            print('An email has been sent to %s' % send_to)
        else:
            print('The email did not send to %s' % send_to)
