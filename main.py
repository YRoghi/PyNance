"""
@author Yann ROGHI

"""
import os
import toolkit

if __name__ == "__main__":
    paths = os.listdir()
    payslip = list()

    for path in paths:
        # Grabs all PDFs from current directory
        if path[-4:].lower() == '.pdf':
            payslip.append(toolkit.Payslip(path))
    for item in payslip:
        print(item.getNetPay())

