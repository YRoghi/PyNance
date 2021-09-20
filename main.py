"""
@author Yann ROGHI

"""
import os
import toolkit

if __name__ == "__main__":

    # ------------------------------- PAYSLIP PARSING -------------------------------
    paths = os.listdir("payslips")
    payslip = list()

    for path in paths:
        # Grabs all PDFs from current directory
        if path[-4:].lower() == '.pdf':
            print(path)
            payslip.append(toolkit.Payslip("payslips/" + path))
            break

    print([item.getPAYD() for item in payslip])

    # ------------------------------- GOOGLE SHEETS -------------------------------
