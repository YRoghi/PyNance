from pdfreader import SimplePDFViewer
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class Payslip:
    """
    Object that stores Net Pay and Total Deductions parsed from standard [REDACTED] payslip format.
    """

    date = None
    net_pay = None
    total_deductions = None
    PAYD = None
    accommodation = None

    def __init__(self, path):

        file = open(path, 'rb')
        viewer = SimplePDFViewer(file)
        viewer.render()
        markdown = viewer.canvas.strings

        # TODO: Tidy up testing
        # Used to see structure of PDFreader output
        # print(markdown)
        # Used for testing uniqueness of phrases in PDF
        # print([x for x in markdown if 'PAYD' in x])

        for i in range(len(markdown)):
            # Scraping values from PDF
            if 'Pay Date' in markdown[i]:
                self.date = markdown[i - 1]
            if 'Total Deductions This Period' in markdown[i]:
                self.net_pay = markdown[i + 1]
                self.total_deductions = markdown[i - 1]
            if 'PAYD' in markdown[i]:
                self.PAYD = markdown[i + 1]
            if 'Tax on Accommodation NCB' in markdown[i]:
                self.accommodation = markdown[i + 1]

        if not self.accommodation:
            self.accommodation = 0

    def getData(self):
        """Returns dictionary containing all attributes pulled from Payslip"""
        return {
            'date': self.date,
            'net_pay': self.net_pay,
            'total_deductions': self.total_deductions,
            'PAYD': self.PAYD,
            'accommodation': self.accommodation,
        }

    def getDate(self):
        """Returns Date attribute"""
        return self.date

    def getNetPay(self):
        """Returns Net Pay attribute"""
        return self.net_pay

    def getTotalDeductions(self):
        """Returns Total Deductions attribute"""
        return self.total_deductions

    def getPAYD(self):
        """Returns PAYD attribute"""
        return self.PAYD

    def getAccommodation(self):
        """Returns NCB attribute"""
        return self.accommodation


class SheetHandler:
    """
    Handles all interactions with the google API
    """

    # If scope changes delete token.json
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = '1ZtdJoKsn-6VPZ449CGSKKU6tOkGDHdxo1t5F2njBD7s'

    service = None
    sheet = None

    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        if not self.service:
            self.service = build('sheets', 'v4', credentials=creds)
            self.sheet = self.service.spreadsheets()
