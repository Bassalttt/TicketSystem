'''
Index:
    Authorization
    AuthorizeationError
    InputError
    TicketDBError
    TicketStatus
    TicketType
    UserIdentity
'''

from enum import Enum

class Authorization(Enum):
    Create = "C"
    Read = "R"
    Update = "U"
    Delete = "D"

class AuthorizeationError(Enum):
    NoAuthorization = 1

class InputError(Enum):
    NoSuchIdentity = 1
    NoSuchOperation = 2
    NoSuchOption = 3

class TicketDBError(Enum):
    TitleFail = 1
    ValueEmpty = 2
    RowError = 3
    ColumnError= 4

    WrongFieldNumber = 5
    WrongFieldContent = 6
    FillInError = 7

class TicketStatus(Enum):
    Waiting = "Waiting"
    Done = "Done"

class TicketType(Enum):
    Bug = "Bug"
    NewFeature = "NewFeature"

class UserIdentity(Enum):
    PM = "PM"
    QA = "QA"
    RD = "RD"
