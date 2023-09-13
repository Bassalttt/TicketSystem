from abc import ABC, abstractmethod
from namespace import TicketStatus, TicketType, UserIdentity
from namespace import Authorization
from ticket_db import TicketFormat

class UserInterface(ABC):
    def __init__(self, name: str, user_identity: UserIdentity) -> None:
        self.name = name
        self.user_identity = user_identity

        self.is_creatable = False
        self.is_readable = False
        self.is_updatable = False
        self.is_deletable = False

        # each attribute is create condition or not
        self.create_condition = TicketFormat(False, False, False, False, False, False)

        # each attribute is read condition or not
        self.read_condition = TicketFormat.Empty()

        # each attribute is updatable or not
        self.update_content = TicketFormat(False, False, False, False, False, False)

        self._set_authorization()

    @abstractmethod
    def _set_authorization(self):
        pass

    def get_authorization(self) -> None:
        user_authorization = ""
        if self.is_creatable:
            user_authorization += "Create(%s)," % Authorization.Create.value

        if self.is_readable:
            user_authorization += "Read(%s), " % Authorization.Read.value

        if self.is_updatable:
            user_authorization += "Update(%s)," % Authorization.Update.value

        if self.is_deletable:
            user_authorization += "Delete(%s)" % Authorization.Delete.value

        return user_authorization

class UserPM(UserInterface):
    def __init__(self, name) -> None:
        super().__init__(name, UserIdentity.PM)

    def _set_authorization(self):
        self.is_creatable = True
        self.is_readable = True
        self.is_updatable = True
        self.is_deletable = True

        #self.read_condition no need to be set. A PM can see every ticket.
        self.update_content.description = True
        self.update_content.assign_to= True
        self.update_content.status = True
        self.update_content.submitter = True
        self.update_content.ticket_type = True

class UserQA(UserInterface):
    def __init__(self, name) -> None:
        super().__init__(name, UserIdentity.QA)

    def _set_authorization(self):
        self.is_creatable = True
        self.is_readable = True
        self.is_updatable = False
        self.is_deletable = False

        self.create_condition.ticket_type = TicketType.Bug

        self.read_condition.submitter = self.name

        #self.update_content no need to be set. A QA cannot update ticket.

class UserRD(UserInterface):
    def __init__(self, name) -> None:
        super().__init__(name, UserIdentity.RD)

    def _set_authorization(self):
        self.is_creatable = False
        self.is_readable = True
        self.is_updatable = True
        self.is_deletable = False

        self.read_condition.assign_to = self.name
        self.read_condition.status = TicketStatus.Waiting.value

        self.update_content.status = TicketStatus.Done.value

