"""
@author Yann ROGHI
"""

import os
from toolkit import Payslip, GoogleHandler, SheetHandler, MailHandler


def main():
    """Directs flow of the script"""

    googleApi = GoogleHandler()

    # Checks for "payslips" local directory
    dir = "payslips"
    if not os.path.exists(dir):
        os.mkdir(dir)

    # ------------------------------- GMAIL HANDLER -------------------------------
    gMail = MailHandler(googleApi.getMailService())
    gMail.getMails()
    gMail.downloadAttachments()

    # ------------------------------- PAYSLIP PARSING -------------------------------
    # Changing current working directory
    relative_path = os.path.dirname(__file__)
    os.chdir(relative_path)
    # Pathing shenanigans from earlier versions
    dirpath = os.path.join(relative_path, 'payslips')
    paths = os.listdir(dirpath)
    payslips = list()

    for path in paths:
        # Grabs all PDFs from current directory
        if path[-4:].lower() == '.pdf':
            payslips.append(Payslip(os.path.join(dirpath, path)))

    # ------------------------------- GOOGLE SHEETS -------------------------------

    # Values to be appended to gSheet
    values = list()

    for payslip in payslips:
        data = payslip.getData()
        values.append([data[key] for key in data])
    body = {
        'values': values
    }

    # Appending to gSheet
    gSheet = SheetHandler(googleApi.getSheetService())
    result = gSheet.service.spreadsheets().values().append(
        spreadsheetId=gSheet.SPREADSHEET_ID, range='A1',
        valueInputOption='USER_ENTERED', body=body).execute()


if __name__ == '__main__':
    main()
