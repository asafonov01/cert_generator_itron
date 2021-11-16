import json
import textwrap
import time

from PyPDF2.pdf import PageObject
from pyrogram import idle, filters, Client
from pyrogram.types import Message
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from textwrap import wrap

from pyrogram import Client
my_tg_client = Client('my_account', api_id=1910146, api_hash='1558300910a39d704a25846b3337bbba')


class PdfGenerator:
    def __init__(self, cert_template_file: str = 'cert2.pdf'):
        cert_template_pdf = PdfFileReader(open(cert_template_file, "rb"))
        self.cert_template_page = cert_template_pdf.getPage(0)
        template_sizes = self.cert_template_page.mediaBox
        self.template_w, self.template_h = float(template_sizes.getWidth()), float(template_sizes.getHeight())

    def _gen_page_with_name(self, surname: str, name: str, title: str = None, leading = 25, y_text_offset = 35, title_offset=5, font_size = 23, title_font_size = 17, one_line: bool = False, bold: bool = False):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, (self.template_w, self.template_h))
        pdfmetrics.registerFont(TTFont('Arial', 'Arial Unicode.ttf'))
        pdfmetrics.registerFont(TTFont('ArialBold', 'arial_bold.ttf'))
        can.setFont('ArialBold' if bold else 'Arial', font_size)

        name_lines = 0

        for i, line in enumerate([surname, name] if not one_line else [f'{surname} {name}']):
            can.drawCentredString(self.template_w/2 , self.template_h/2 + y_text_offset - i*leading, line)
            name_lines = i

        if title:
            can.setFont('Arial', title_font_size)
            for i, line in enumerate(textwrap.wrap(title, 60)):
                can.drawCentredString(self.template_w / 2, self.template_h / 2 + y_text_offset - (i + name_lines + 1) * leading - title_offset, line)

        can.save()
        packet.seek(0)
        return PdfFileReader(packet)

    def gen_cert_with_name(self, surname: str, name: str, title: str = None, leading = 25, y_text_offset = 35, title_offset=5, font_size = 23, title_font_size = 17, one_line: bool = False, bold: bool = False):
        result_page = PageObject.createBlankPage(None, self.template_w,
                                                 self.template_h)
        result_page.mergePage(self.cert_template_page)
        result_page.mergePage(self._gen_page_with_name(surname, name, title, leading, y_text_offset, title_offset, font_size, title_font_size, one_line, bold).getPage(0))

        result_pdf = PdfFileWriter()
        result_pdf.addPage(result_page)
        return result_pdf


cert_gen = PdfGenerator()
invite_gen = PdfGenerator('invite.pdf')
cert2_gen = PdfGenerator('cert3.pdf')


@my_tg_client.on_message(filters.command('gen'))
def gen_cert(app: Client, msg: Message):
    name = msg.text[5:]

    surname, name = name.split(' ', maxsplit=1)

    pdf = cert_gen.gen_cert_with_name(surname, name, bold=True, font_size=18)

    result_file_name = f'{surname} {name}.pdf'
    with open(result_file_name, "wb") as file:
        pdf.write(file)

    msg.reply_document(result_file_name)


@my_tg_client.on_message(filters.command('invite'))
def gen_invite(app: Client, msg: Message):
    name = msg.text[8:]

    surname, name = name.split(' ', maxsplit=1)

    pdf = invite_gen.gen_cert_with_name(surname, name, y_text_offset=145, font_size=13, leading=17, one_line=True)

    result_file_name = f'{surname} {name}.pdf'
    with open(result_file_name, "wb") as file:
        pdf.write(file)

    msg.reply_document(result_file_name)


@my_tg_client.on_message(filters.command('cert'))
def gen_c2(app: Client, msg: Message):
    name = msg.text[6:]

    surname, first_name, middle_name, title = name.split(' ', maxsplit=3)
    name = f'{first_name} {middle_name}'

    pdf = cert2_gen.gen_cert_with_name(surname, name, title, y_text_offset=43, title_offset=5, leading=15, font_size=18, one_line=True, bold=True, title_font_size=13)

    result_file_name = f'{surname} {name}.pdf'
    with open(result_file_name, "wb") as file:
        pdf.write(file)

    msg.reply_document(result_file_name)


if __name__ == '__main__':
    my_tg_client.run()