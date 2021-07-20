from pdfreader import SimplePDFViewer


class Payslip:
    """
    Object that stores Net Pay and Total Deductions parsed from standard [REDACTED] payslip format.
    """

    net_pay = None
    total_deductions = None

    def __init__(self, path):

        file = open(path, 'rb')
        viewer = SimplePDFViewer(file)
        viewer.render()
        markdown = viewer.canvas.strings
        for i in range(len(markdown)):
            if 'Total Deductions This Period' in markdown[i]:
                self.net_pay = markdown[i + 1]
                self.total_deductions = markdown[i - 1]

    def getNetPay(self):
        """Returns Net Pay attribute"""
        return self.net_pay

    def getTotalDeductions(self):
        """Returns Total Deductions attribute"""
        return self.total_deductions




