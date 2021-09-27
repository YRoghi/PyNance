from pdfreader import SimplePDFViewer
import os
import json
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class Payslip:
    """
    Object that stores Net Pay and Total Deductions parsed from a standard payslip format.

    Attributes:
        date -- date of the payslip
        net_pay -- amount paid out
        total_deductions -- total deducted from gross salary
        PAYD -- PAYD deduction
        accommodation -- accommodation deduction
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

        for i in range(len(markdown)):
            # Scraping values from PDF
            if 'Pay Date' in markdown[i]:
                self.date = markdown[i - 1]
            if 'Total Deductions This Period' in markdown[i]:
                self.net_pay = markdown[i + 1]
                self.total_deductions = markdown[i - 1]
            if 'PAYD' in markdown[i]:
                self.PAYD = markdown[i + 1]
            if 'Tax on Accommodation' in markdown[i]:
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


class GoogleHandler:

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/spreadsheets',
    ]
    mailService = None
    sheetService = None

    def __init__(self):

        # Most of this is taken from the Quickstart.py scripts provided by the Google API Docs

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

        self.mailService = build('gmail', 'v1', credentials=creds)
        self.sheetService = build('sheets', 'v4', credentials=creds)

    def getMailService(self):
        """
        Returns mail service.
        """

        if self.mailService:
            return self.mailService
        else:
            raise ValueError("Missing Gmail Service from Google.")

    def getSheetService(self):
        """
        Returns sheet service.
        """

        if self.sheetService:
            return self.sheetService
        else:
            raise ValueError("Missing Sheet service from Google.")


class MailHandler:
    """
    Handles interactions with the Gmail API
    """

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    service = None
    messages = None

    def __init__(self, service):
        self.service = service

    def getMails(self):
        """
        Gets mails based on a search filter
        """
        # Obfuscating filter
        if os.path.exists('redacted.json'):
            f = open('redacted.json')
            data = json.load(f)
            flt = data['filter']
        else:
            raise IOError('redacted.json is missing!')

        # Call the Gmail API
        results = self.service.users().messages().list(userId='me', q=flt).execute()
        self.messages = results.get('messages', [])

        if not self.messages:
            raise RuntimeWarning('No messages found.')

        return 0

    def downloadAttachments(self):
        """
        Downloads all attachments based
        """
        for message in self.messages:
            txt = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            attachmentName = txt['payload']['parts'][1]['filename']
            attachmentId = txt['payload']['parts'][1]['body']['attachmentId']
            mailAttachment = self.service.users().messages().attachments().get(
                id=attachmentId,
                messageId=message['id'],
                userId='me'
            ).execute()
            data = bytes(mailAttachment['data'], 'utf-8')
            decoded = base64.urlsafe_b64decode(data)
            if decoded[0:4] != b'%PDF':
                raise ValueError('Missing the PDF file signature')
            f = open("payslips/" + attachmentName, 'wb')
            f.write(decoded)
            f.close()

        return 0


class SheetHandler:
    """
    Handles all interactions with the Google Sheets API
    """

    # If scope changes delete token.json
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = None
    service = None
    sheet = None

    def __init__(self, service):

        # Obfuscating spreadsheet ID
        if os.path.exists('redacted.json'):
            f = open('redacted.json')
            data = json.load(f)
            self.SPREADSHEET_ID = data['id']
        else:
            raise IOError('redacted.json is missing!')

        self.service = service
        self.sheet = self.service.spreadsheets()
