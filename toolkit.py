from pdfreader import SimplePDFViewer


class Payslip:
    """
    Object that stores Net Pay and Total Deductions parsed from standard [REDACTED] payslip format.
    """

    net_pay = None
    total_deductions = None
    PAYD = None

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
            if 'Total Deductions This Period' in markdown[i]:
                self.net_pay = markdown[i + 1]
                self.total_deductions = markdown[i - 1]
            if 'PAYD' in markdown[i]:
                self.PAYD = markdown[i + 1]

    def getNetPay(self):
        """Returns Net Pay attribute"""
        return self.net_pay

    def getTotalDeductions(self):
        """Returns Total Deductions attribute"""
        return self.total_deductions

    def getPAYD(self):
        """Returns PAYD attribute"""
        return self.PAYD




