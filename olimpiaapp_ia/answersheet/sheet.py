from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from dataclasses import dataclass
from io import BytesIO
from .qr import create_qr

# dataclass for AnswerSheet configuration
@dataclass
class SheetConfig:
    width: int # sheet width
    height: int # sheet height
    margin_x: int # left margin
    margin_y: int # top margin
    circle_diameter: int # diameter of each circle
    circle_x_corec: int # correction 
    spacing_x: int # space between question options
    spacing_y: int # space between each question on the same column
    num_column: int # number of each column for each page
    column_split: int # max number of questions per column
    column_gap: int # space between each column
    max_question_page: int # maximum number of questions per page
    space_number_option: int # space between question number and its options
    qr_width: int 
    qr_height: int


class AnswerSheet:
    def __init__(self, list_codes: list[str] | tuple[str], num_questions: int, 
                 num_options: int, filename: str = "sheet.pdf",
                 warning_message: str = 'No dibujar aqui.'):
        """
        docstring
        """

        # list_codes validation
        if not isinstance(list_codes, (list, tuple)):
            raise TypeError(f"List of codes must be a list or tuple, not {type(list_codes).__name__}")

        # num_questions validation
        if not isinstance(num_questions, int):
            raise TypeError(f"Number of questions must be an integer, not {type(num_questions).__name__}.")
        if num_questions < 1:
            raise ValueError("Number of questions must be greater than 0.")
        
        # num_options validation
        if not isinstance(num_options, int):
            raise TypeError(f"Number of options must be an integer, not {type(num_options).__name__}.")
        if num_options < 1:
            raise Exception("Number of options must be greater than 0.")
        
        # filename validation
        if not isinstance(filename, str):
            raise ValueError(f"filename is must be a string, not {type(filename).__name__}.")
        
        self.list_codes = tuple(list_codes)
        self.num_questions = num_questions
        self.num_options = num_options
        self.filename = filename
        self.warning_msg = warning_message

        # set init config
        self.canvas = canvas.Canvas(self.filename, pagesize=letter)
        self.config: SheetConfig = SheetConfig(
            width=letter[0],
            height=letter[1],
            margin_x=60,
            margin_y=80,
            circle_diameter=9,
            circle_x_corec=3,
            spacing_x=40,
            spacing_y=42,
            num_column=2,
            column_split=16,
            column_gap=270,
            max_question_page=30,
            space_number_option=20,
            qr_width=70,
            qr_height=70
        )

    def __str__(self) -> str:
        raise NotImplementedError()
    
    def encrypt_code(self, code: str, first_question_number: int, last_question_number: int) -> str:
        """
        docstring
        """
        return f'{code},{first_question_number},{last_question_number};'

    def generate(self) -> None:
        """
        docstring
        """

        def insert_qr(code: str) -> None:
            buffer = BytesIO()
            create_qr(f'{code}').save(buffer, format="PNG")
            buffer.seek(0)

            self.canvas.drawBoundary(
                sb=1,
                x1=self.config.width - self.config.column_gap, 
                y1=self.config.margin_y - 10,
                width=self.config.column_gap - self.config.margin_x, 
                height=self.config.qr_height
            )

            self.canvas.drawString(
                x=self.config.width - self.config.column_gap + 10,
                y=self.config.margin_y - 10 + (self.config.qr_height / 2) - 6,
                text=f'{self.warning_msg}',
            )
            
            self.canvas.drawImage(
                image=ImageReader(buffer),
                x=self.config.width - self.config.margin_x - self.config.qr_width,
                y=self.config.margin_y - 10,
                width=self.config.qr_width,
                height=self.config.qr_height,
            )

        # for each code, generate their own page of answers
        for code in self.list_codes:
            
            coord_x: int = self.config.margin_x # first column
            coord_y: int = self.config.height - self.config.margin_y
            count_column: int = 0
            first_q, last_q = 1, 0

            for i in range(self.num_questions):
                count_column += 1
                # print question number
                self.canvas.setFont("Helvetica", 12)
                self.canvas.drawString(
                    x=coord_x,
                    y=coord_y,
                    text=f'{i + 1}.'
                )

                # print question options
                coord_x += self.config.space_number_option + 30
                for j in range(self.num_options):
                    self.canvas.circle(
                        x_cen=coord_x, 
                        y_cen=coord_y + 3, 
                        r=self.config.circle_diameter
                    )
                    
                    self.canvas.drawCentredString(
                        x=coord_x, 
                        y=coord_y,
                        text=chr(65 + j)
                    )
                    coord_x += self.config.spacing_x

                # page change
                if (i + 1) % self.config.max_question_page == 0:
                    insert_qr(self.encrypt_code(code, first_q, i + 2))

                    if (i + 1) == self.num_questions:
                        break

                    count_column = 0
                    first_q = i + 2
                    # reset cordenates
                    coord_x: int = self.config.margin_x
                    coord_y: int = self.config.height - self.config.margin_y
                    self.canvas.showPage()
                    continue

                # fix coords
                coord_x -= self.config.space_number_option + 30 + (self.num_options * self.config.spacing_x)
                coord_y -= self.config.spacing_y

                # column change
                if count_column == self.config.column_split:
                    count_column = 0
                    coord_x += self.config.column_gap
                    coord_y = self.config.height - self.config.margin_y # reset

            insert_qr(self.encrypt_code(code, first_q, i + 2))

            self.canvas.showPage()

    def save(self) -> None:
        """
        docstring
        """
        
        self.canvas.save()