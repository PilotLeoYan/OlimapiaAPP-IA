from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
from .qr import create_qr
from .sheetconfig import SheetConfig


class AnswerSheet:
    def __init__(self, list_codes, num_questions, num_options, filename='sheet.pdf',
                 fontname='Times-Roman', fontsize=12):
        # list of codes validation
        if not isinstance(list_codes, (list, tuple)): # type: ignore
            raise TypeError(f'List of codes must be a list or tuple, not {type(list_codes).__name__}.')
        
        # number of questions validation
        if not isinstance(num_questions, int): # type: ignore
            raise TypeError(f'Number of questions must be a int or float, not {type(num_questions).__name__}.')
        if num_questions < 1:
            raise ValueError(f'Numbe rof questions must be greater than 0, received {num_questions}.')
        
        # number of options validation
        if not isinstance(num_options, int): # type: ignore
            raise TypeError(f'Number of options must be a int or float, not {type(num_options).__name__}.')
        if num_options < 1:
            raise ValueError(f'Number of options must be greater than 0, received {num_options}.')
        
        # filename or path validation
        if not isinstance(filename, str): # type: ignore
            raise TypeError(f'File name or path must be a str, not {type(filename).__name__}.')
        
        # font name validation
        if not isinstance(fontname, str): # type: ignore
            raise TypeError(f'Font name must be a str, not {type(fontname).__name__}.')
        
        # font size validation
        if not isinstance(fontsize, (int, float)): # type: ignore
            raise TypeError(f'Font size must be a int or float, not {type(fontsize).__name__}.')

        self.list_codes = tuple(list_codes)
        self.n_questions = num_questions
        self.n_options = num_options
        self.filename = filename

        self.text_title: None | str = None
        self._title: bool = False # check if a title is applied

        self.logo_path: None | str = None
        self._logo: bool = False # chech if a logo is apllied

        self._border: bool = False
        self._y_line: bool = False

        self._numeration: None | int = None

        self.canvas = canvas.Canvas(self.filename, letter)
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
            spacing_x=None, # type: ignore
            questions_per_column=None, # type: ignore
            max_questions_per_page=None, # type: ignore
            circle_y_offset=None, # type: ignore
        )

        self.config.spacing_x = ((self.config.width - 2 * self.config.margin_x) // 2 + 1 + self.config.fontsize - (self.n_options * (self.config.circle_diameter + self.config.option_spacing))) // 2
        self.config.questions_per_column = int((self.config.height - 2 * self.config.margin_y) // (self.config.spacing_y))
        self.config.max_questions_per_page = 2 * self.config.questions_per_column - 2
        self.config.circle_y_offset = self.config.fontsize - self.config.circle_diameter + 1

    def __str__(self) -> str:
        s: str = fr'''list of codes: {self.list_codes}
number of questions: {self.n_questions}
number of options: {self.n_options}
filename: {self.filename}

sheet configuration
    sheet size: Letter, width={self.config.width}, height={self.config.height}
    margin x: {self.config.margin_x}
    margin y: {self.config.margin_y}
    font name: "{self.config.fontname}"
    font size: {self.config.fontsize}
    spacing x: {self.config.spacing_x}
    spacing y: {self.config.spacing_y}
    circle diameter: {self.config.circle_diameter}
    circle y offset: {self.config.circle_y_offset}
    option spacing: {self.config.option_spacing}
    questions per columns: {self.config.questions_per_column}
    maximum of questions per page: {self.config.max_questions_per_page}
    QR Code: width={self.config.qr_width}, height={self.config.qr_height}

Optional configuration
    title: {f'True, text="{self.text_title}"' if self._title else 'False'}
    logo: {fr'True, path="{self.logo_path}"' if self._logo else 'False'}
    border: {self._border}
    vertical line: {self._y_line}'''
        
        return s

    def __drawTitle__(self) -> None:
        if not self._title:
            return
        
        titlesize = 26

        self.canvas.setFont(self.config.fontname, titlesize)
        self.canvas.drawCentredString(
            x=self.config.width // 2,
            y=self.config.height - self.config.margin_y - titlesize - 10,
            text=self.text_title # type: ignore
        )

        self.canvas.setFont(self.config.fontname, self.config.fontsize)

    def __drawLogo__(self) -> None:
        if not self._logo:
            return

        if self._title:
            self.canvas.drawImage( # type: ignore
                image=self.logo_path, 
                x=self.config.margin_x,
                y=self.config.height - self.config.margin_y - 26 * 2,
                width=26 * 2,
                height=26 * 2
            )
        else:
            self.canvas.drawImage( # type: ignore
                image=self.logo_path, 
                x=self.config.width // 2 + self.config.spacing_x,
                y=self.config.margin_y + 26 // 2,
                width=26 * 2,
                height=26 * 2
            )

    def __drawBorder__(self) -> None:
        if not self._border:
            return

        self.canvas.drawBoundary( # type: ignore
            sb=0.5, x1=self.config.margin_x, y1=self.config.margin_y,
            width=self.config.width - 2 * self.config.margin_x,
            height=self.config.height - 2 * self.config.margin_y
        )

    def __drawVerticalLine__(self) -> None:
        if not self._y_line:
            return

        self.canvas.line(
            x1=self.config.width // 2,
            y1=self.config.margin_y + (0 if self._numeration is None else 12),
            x2=self.config.width // 2,
            y2=self.config.height - self.config.margin_y - (26 * 2 if self._title else 0)
        )

    def __drawNumeration__(self) -> None:
        if self._numeration is None:
            return
        
        self.canvas.drawCentredString(
            x=self.config.width // 2,
            y=self.config.margin_y + 2,
            text=f'{self._numeration}'
        )

        self._numeration += 1

    def __drawPageFormat__(self) -> None:
        self.__drawTitle__()
        self.__drawLogo__()

        self.__drawBorder__()
        self.__drawVerticalLine__()

        self.__drawNumeration__()

    def __drawQRCode__(self, string: str) -> None:
        buffer = BytesIO()
        create_qr(f'{string}').save(buffer, format="PNG")
        buffer.seek(0)

        self.canvas.drawImage( # type: ignore
            image=ImageReader(buffer),
            x=self.config.width - self.config.margin_x - self.config.qr_width - 2 * self.config.spacing_x,
            y=self.config.margin_y + 26 // 2,
            width=self.config.qr_width,
            height=self.config.qr_height,
        )

    def __drawQuestions__(self, code: str) -> None:
        x_coord: float = self.config.margin_x + self.config.spacing_x
        y_coord: float = self.config.height - self.config.margin_y - self.config.spacing_y - (26 * 2 if self._title else 0)
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
                self.canvas.circle(x_coord, y_coord + self.config.circle_y_offset, r=self.config.circle_diameter) # type: ignore

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

    @property
    def title(self):
        return self.text_title

    @title.setter
    def title(self, title: str):

        self.text_title = title
        self._title = True

        self.config.questions_per_column -= 1
        self.config.max_questions_per_page -= 2

    @property
    def logo(self):
        return self.logo_path

    @logo.setter
    def logo(self, logo_path: str):
        self.logo_path = logo_path
        self._logo = True

    def border(self):
        self._border = True

    def verticalLine(self):
        self._y_line = True

    def numeration(self, start=1):
        if not isinstance(start, int):
            raise TypeError(f'Start must be a int, not {type(start).__name__}.')

        self._numeration = start

    def generate(self) -> None:
        for code in self.list_codes:
            self.__drawNewPage__(code)
            self.canvas.showPage()

    def save(self) -> None:
        self.canvas.save()