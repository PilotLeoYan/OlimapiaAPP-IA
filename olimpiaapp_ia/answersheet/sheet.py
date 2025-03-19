from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from dataclasses import dataclass
from io import BytesIO
from .qr import create_qr


@dataclass
class SheetConfig:
    width: int  # Sheet width
    height: int  # Sheet height
    margin_x: int
    margin_y: int
    fontname: str
    fontsize: int
    spacing_x: int
    spacing_y: int
    circle_diameter: int
    circle_y_offset: int
    option_spacing: int
    questions_per_column: int
    max_questions_per_page: int
    qr_width: int
    qr_height: int


class AnswerSheet:
    def __init__(self, list_codes: list[str] | tuple[str], num_questions: int,
                 num_options: int, 
                 fontname: str = 'Times-Roman', fontsize: int = 12):

        self.list_codes = list_codes
        self.n_questions = num_questions
        self.n_options = num_options

        self.title: None | str = None
        self._title: bool = False

        self.canvas = canvas.Canvas('test.pdf', letter)
        self.config = SheetConfig(
            width=letter[0],
            height=letter[1],
            margin_x=24,
            margin_y=24,
            fontname=fontname,
            fontsize=fontsize,
            spacing_y=42,
            circle_diameter=9,
            option_spacing=40,
            qr_width=70,
            qr_height=70,
            # - - -
            spacing_x=None,
            questions_per_column=None,
            max_questions_per_page=None,
            circle_y_offset=None,
        )

        self.config.spacing_x = ((self.config.width - 2 * self.config.margin_x) // 2 + 1 + self.config.fontsize - (self.n_options * (self.config.circle_diameter + self.config.option_spacing))) // 2
        self.config.questions_per_column = int((self.config.height - 2 * self.config.margin_y) // (self.config.spacing_y))
        self.config.max_questions_per_page = 2 * self.config.questions_per_column - 2
        self.config.circle_y_offset = self.config.fontsize - self.config.circle_diameter + 1

    def __drawTitle__(self) -> None:
        if not self._title:
            return
        
        titlesize = 26
        
        # title area
        self.canvas.drawBoundary(
            sb=0.5, 
            x1=self.config.margin_x,
            y1=self.config.height - self.config.margin_y,
            width=self.config.width - 2 * self.config.margin_x,
            height=- 2 * titlesize
        )

        self.canvas.setFont(self.config.fontname, titlesize)
        self.canvas.drawCentredString(
            x=self.config.width // 2,
            y=self.config.height - self.config.margin_y - titlesize,
            text=self.title
        )

        self.canvas.setFont(self.config.fontname, self.config.fontsize)

    def __drawPageFormat__(self) -> None:
        self.__drawTitle__()

        # margin
        self.canvas.drawBoundary(
            sb=0.5, x1=self.config.margin_x, y1=self.config.margin_y,
            width=self.config.width - 2 * self.config.margin_x,
            height=self.config.height - 2 * self.config.margin_y
        )

        self.canvas.line(
            x1=self.config.width // 2,
            y1=self.config.margin_y,
            x2=self.config.width // 2,
            y2=self.config.height - self.config.margin_y - (26 * 2 if self._title else 0)
        )

    def __drawQRCode__(self, string: str) -> None:
        buffer = BytesIO()
        create_qr(f'{string}').save(buffer, format="PNG")
        buffer.seek(0)

        self.canvas.drawImage(
            image=ImageReader(buffer),
            x=self.config.width - self.config.margin_x - self.config.qr_width,
            y=self.config.margin_y,
            width=self.config.qr_width,
            height=self.config.qr_height,
        )
        print(string)

    def __drawQuestions__(self, code: str) -> None:
        x_coord: int = self.config.margin_x + self.config.spacing_x
        y_coord: int = self.config.height - self.config.margin_y - self.config.spacing_y - (26 * 2 if self._title else 0)
        question_count: int = 0
        start: int = 1

        for i in range(1, self.n_questions + 1):
            # draw question number
            self.canvas.drawString(x_coord, y_coord, text=f'{i}.')
            question_count += 1

            # draw question options
            for j in range(self.n_options):
                x_coord += self.config.option_spacing
                # draw question option letter
                self.canvas.drawCentredString(x=x_coord, y=y_coord, text=chr(65 + j))
                # draw circle
                self.canvas.circle(x_coord, y_coord + self.config.circle_y_offset, r=self.config.circle_diameter)

            # page change
            if question_count == self.config.max_questions_per_page:
                if i == self.n_questions:
                    break

                self.__drawQRCode__(f'{code},{start},{i + 1};')
                start = i + 1

                self.canvas.showPage()
                self.__drawPageFormat__()

                # reset values
                x_coord = self.config.margin_x + self.config.spacing_x
                y_coord = self.config.height - self.config.margin_y - self.config.spacing_y - (26 * 2 if self._title else 0)
                question_count = 0
                continue

            # column change
            if question_count == self.config.questions_per_column:
                x_coord = self.config.width // 2 + self.config.spacing_x
                y_coord= self.config.height - self.config.margin_y - self.config.spacing_y - (26 * 2 if self._title else 0)
                continue

            x_coord -= self.n_options * self.config.option_spacing
            y_coord -= self.config.spacing_y

        self.__drawQRCode__(f'{code},{start},{self.n_questions + 1};')

    def __drawNewPage__(self, code: str) -> None:
        self.__drawPageFormat__()

        self.canvas.setFont(self.config.fontname, self.config.fontsize)
        self.__drawQuestions__(code)

    def addTitle(self, title: str) -> None:
        self.title = title
        self._title = True

        self.config.questions_per_column -= 1
        self.config.max_questions_per_page -= 2

    def generate(self) -> None:
        for code in self.list_codes:
            self.__drawNewPage__(code)
            self.canvas.showPage()

    def save(self) -> None:
        self.canvas.save()