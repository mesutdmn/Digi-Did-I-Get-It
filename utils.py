import magic
import re
import random

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import markdown2

data_types = {"pdf":"application/pdf",
              "txt":"text/plain",
              "mp3":"audio/mpeg",
              "enex":"text/xml",
              "mp4":"video/mp4",
              "mpeg4":"video/mp4",
              "docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              "png":"image/png",
              "jpg":"image/jpeg",
              "jpeg":"image/jpeg",
              "pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
              "epub":"application/epub+zip"}

def check_file_type(file):
    """Check if the file is of the correct type"""
    file_content = file.read()
    file_extension = file.name.split('.')[-1].lower()

    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file_content)

    print(f"File MIME: {file_mime}")
    return file_mime == data_types[file_extension]


def extract_youtube_id(url):
    """Extract the YouTube video ID from a URL"""
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.*|(?:v|e(?:mbed)?|watch|watch\?.*v=)|.*[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'

    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


def shuffle_choices(question_data):
    """
    Takes a list of question dictionaries and shuffles the choices and answers, while ensuring
    the labels remain in 'A', 'B', 'C', 'D' format and only one answer is marked True.
    """
    updated_questions = []

    for question in question_data:
        choices = question['choices']
        answers = question['answers']

        choice_answer_pairs = list(zip(choices, answers))
        random.shuffle(choice_answer_pairs)

        shuffled_choices, shuffled_answers = zip(*choice_answer_pairs)

        # Re-label choices as A, B, C, D
        labeled_choices = [f"{label}) {choice}" for label, choice in zip(['A', 'B', 'C', 'D'], shuffled_choices)]

        updated_question = {
            'question': question['question'],
            'choices': labeled_choices,
            'answers': list(shuffled_answers),
            'explain': question['explain']
        }

        updated_questions.append(updated_question)

    return updated_questions



def create_pdf(data):
    """Create a PDF file from a list of question dictionaries"""
    doc = SimpleDocTemplate("questions.pdf", pagesize=A4, title="Questions and Answers",
                             topMargin=0.5 * inch, bottomMargin=0.5 * inch)

    elements = []

    pdfmetrics.registerFont(TTFont('Arial-Unicode', './style/arial-unicode-ms.ttf'))

    elements.append(Paragraph(
        "Questions",
        ParagraphStyle(
            name='CenteredTitle',
            fontName='Arial-Unicode',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=0.5 * inch
        )
    ))

    main_table_data = []

    for index, item in enumerate(data, start=1):
        question = f"Q{index}:{item['question']}"

        question_paragraph = Paragraph(markdown2.markdown(question), ParagraphStyle(
            name='Normal',
            fontName='Arial-Unicode',
            fontSize=9,
            leading=12,
            spaceAfter=0.1 * inch,
        ))

        choices_data = [[question_paragraph]]
        for i, choice in enumerate(item["choices"]):
            choice_paragraph = Paragraph(f"{chr(65 + i)}) {markdown2.markdown(choice[2:])}", ParagraphStyle(
                name='Normal',
                fontName='Arial-Unicode',
                fontSize=9,
                leading=12,
                spaceAfter=0.1 * inch
            ))
            choices_data.append([choice_paragraph])

        if index % 2 == 1:
            main_table_data.append([choices_data, ""])
        else:
            main_table_data[-1][1] = choices_data

    main_table = Table(main_table_data, colWidths=[285, 285])
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('FONT', (0, 0), (-1, 0), 'Arial-Unicode'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('VALIGN', (0, 0), (-1, 0), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('FONT', (0, 1), (-1, -1), 'Arial-Unicode'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(main_table)
    elements.append(PageBreak())

    elements.append(Paragraph(
        "Answers",
        ParagraphStyle(
            name='CenteredTitle',
            fontName='Arial-Unicode',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=0.5 * inch
        )
    ))

    answer_key_data = []
    row = []
    for index, item in enumerate(data, start=1):
        correct_index = item['answers'].index(True)
        answer_text = f"Soru {index}: {item['choices'][correct_index][0]}"
        row.append(answer_text)

        if index % 5 == 0:
            answer_key_data.append(row)
            row = []

    if row:
        answer_key_data.append(row)

    answer_key_table = Table(answer_key_data, colWidths=[100] * 5)
    answer_key_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONT', (0, 0), (-1, -1), 'Arial-Unicode'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ]))

    elements.append(answer_key_table)

    doc.build(elements)

