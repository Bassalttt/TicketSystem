'''
Index:
    TicketFormat
    SheetColumn
    GetSheetColumnInterface
    NormalGetSheetColumn
    TestGetSheetColumn
    ParseTicketDB
    WriteDB
    TestParseTicketDB_
'''

from abc import ABC, abstractmethod
import unittest

from xlrd import open_workbook
from openpyxl import Workbook

from error_handler import TicketDBException
from namespace import TicketDBError, TicketStatus, TicketType

TICKET_FILE = ''

class TicketFormat():
    '''Ticket format'''
    def __init__(self,
                title:str='',
                description:str='',
                assign_to:str='',
                status:str=TicketStatus.Waiting.value,
                submitter:str='',
                ticket_type:str=TicketType.Bug.value) -> None:
        self.title = title
        self.description = description
        self.assign_to= assign_to
        self.status = status
        self.submitter = submitter
        self.ticket_type = ticket_type

    @staticmethod
    def Empty():
        '''Clear the format.'''
        return TicketFormat(False, False, False, False, False, False)

# ------ Parse Ticket ------
class SheetColumn():
    '''Sheet column.'''
    def __init__(self) -> None:
        self.title = -1
        self.description = -1
        self.assign_to= -1
        self.status = -1
        self.submitter = -1
        self.ticket_type = -1

    def assign_value(self, title, descrip, assign, status, submitter, t_type):
        '''Assign values to the field.'''
        self.title = title
        self.description = descrip
        self.assign_to = assign
        self.status = status
        self.submitter = submitter
        self.ticket_type = t_type

class GetSheetColumnInterface(ABC):
    @abstractmethod
    def get_sheet_column(self, data_sheet):
        pass


class NormalGetSheetColumn(GetSheetColumnInterface):
    def get_sheet_column(self, data_sheet) -> SheetColumn:
        for i, item in enumerate(data_sheet.row_values(0)):
            if item == 'title':
                title_column = i
            elif item == 'description':
                description_column = i
            elif item == 'assign_to':
                assign_to_column = i
            elif item == 'status':
                status_column = i
            elif item == 'submitter':
                submitter_column = i
            elif item == 'type':
                ticket_type_column = i

        sheet_column = SheetColumn()
        sheet_column.assign_value(title_column,
                                description_column,
                                assign_to_column,
                                status_column,
                                submitter_column,
                                ticket_type_column)
        return sheet_column

class TestGetSheetColumn(GetSheetColumnInterface):
    def get_sheet_column(self, data_sheet) -> SheetColumn:
        sheet_column = SheetColumn()
        sheet_column.assign_value(0, 1, 2, 3, 4, 5)
        return sheet_column

class ParseTicketDB():
    def __init__(self,
                file_path: str,
                get_sheet_column_interface: GetSheetColumnInterface) -> None:
        self.__data_sheet = self.__get_data_sheet(file_path)
        self.__all_ticket = []

        self.get_sheet_column = get_sheet_column_interface
        self.sheet_title_column = None # SheetColumn()

    def __get_data_sheet(self, file_path: str):
        work_book = open_workbook(file_path)
        return work_book.sheet_by_name("Sheet")

    def get_column(self) -> None:
        self.sheet_title_column = self.get_sheet_column.get_sheet_column(self.__data_sheet)
        return self.sheet_title_column

    def __get_cell_value(self, row: int, column: int) -> str:
        if not isinstance(row, int):
            raise TicketDBException(TicketDBError.RowError)
        elif row < 0:
            raise TicketDBException(TicketDBError.RowError)

        if column == -1:
            raise TicketDBException(TicketDBError.TitleFail)
        elif column < 0:
            raise TicketDBException(TicketDBError.ColumnError)

        value = self.__data_sheet.cell_value(row, column)
        if value == '':
            raise TicketDBException(TicketDBError.ValueEmpty)
        else:
            return value

    def __parse_content(self) -> None:
        for i in range(1, self.__data_sheet.nrows):
            title = self.__get_cell_value(i, self.sheet_title_column.title)
            description = self.__get_cell_value(i, self.sheet_title_column.description)

            assign_to = self.__get_cell_value(i, self.sheet_title_column.assign_to)
            status = self.__get_cell_value(i, self.sheet_title_column.status)
            submitter = self.__get_cell_value(i, self.sheet_title_column.submitter)
            ticket_type = self.__get_cell_value(i, self.sheet_title_column.ticket_type)

            self.__all_ticket.append(
                TicketFormat(title, description, assign_to, status, submitter, ticket_type))

    def get_content(self) -> list:
        self.get_column()
        self.__parse_content()
        return self.__all_ticket

# ------ Write Ticket ------

class WriteDB():
    def __init__(self, ticket: TicketFormat)-> None:
        self.__ticket = ticket

    def fill_in(self, ticket_file) -> None:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet['A1'] = 'title'
        worksheet['B1'] = 'description'
        worksheet['C1'] = 'assign_to'
        worksheet['C1'] = 'assign_to'
        worksheet['D1'] = 'status'
        worksheet['E1'] = 'submitter'
        worksheet['F1'] = 'type'
        for i, ticket in enumerate(self.__ticket):
            row_num = str(i + 2)
            worksheet['A'+row_num] = ticket.title
            worksheet['B'+row_num] = ticket.description
            worksheet['C'+row_num] = ticket.assign_to
            worksheet['D'+row_num] = ticket.status
            worksheet['E'+row_num] = ticket.submitter
            worksheet['F'+row_num] = ticket.ticket_type

        workbook.save(ticket_file)

# ------ Unit Test ------

class TestParseTicketDB_(unittest.TestCase):
    def test_normal_prase_ticket_db(self):
        get_sheet_column_interface = NormalGetSheetColumn()
        parse_ticket_db = ParseTicketDB(TICKET_FILE, get_sheet_column_interface)

        result = parse_ticket_db.get_column()
        self.assertEqual(result.title, 0)

    def test_parse_ticket_basic(self):
        get_sheet_column_interface = TestGetSheetColumn()
        parse_ticket_db = ParseTicketDB(TICKET_FILE, get_sheet_column_interface)

        result = parse_ticket_db.get_column()
        self.assertEqual(result.title, 0)

if __name__ == '__main__':
    unittest.main()
