from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph


class LegalDoc:
    def __init__(self, path):

        self.path = path

        styles = getSampleStyleSheet()
        self._styleN = styles["Normal"]
        self._styleH1 = styles["Heading1"]
        self._styleH2 = styles["Heading2"]
        self.page = 0

        doc = BaseDocTemplate(self.path, pagesize=A4)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 2 * cm, id="normal")
        template = PageTemplate(id="legal_doc", frames=frame, onPage=self.header_footer)
        doc.addPageTemplates([template])

        text = []
        for i in range(111):
            text.append(Paragraph("This is line %d." % i, self._styleN))

        doc.build(text)

    def header_footer(self, canvas, doc):
        self.page += 1

        canvas.saveState()
        P = Paragraph("This is a multi-line header.  It goes on every page.  " * 2, self._styleN)
        w, h = P.wrap(doc.width, doc.topMargin)
        P.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        canvas.restoreState()

        canvas.saveState()
        P = Paragraph("This is a multi-line footer:%s.  It goes on every page.  " % self.page, self._styleN)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()
