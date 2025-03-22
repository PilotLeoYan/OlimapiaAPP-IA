from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from dataclasses import dataclass
from io import BytesIO
from .qr import create_qr


@dataclass
class SheetConfig:
    """Configuration for the question and answer sheet in the PDF."""

    width: int  # Sheet width
    height: int  # Sheet height
    margin_x: int # Horizontal margin
    margin_y: int # Vertical margin
    fontname: str # Font name
    fontsize: int # Font size
    spacing_x: int # Horizontal space between answer and sheet
    spacing_y: int # Vertical space between each asnwer
    circle_diameter: int # Circle diameter or Burble diameter
    circle_y_offset: int # Vertical offset of the burble (correction)
    option_spacing: int # Space between each burble
    questions_per_column: int # Maximun of questions per column
    max_questions_per_page: int # Maximum questions per page
    qr_width: int # QR code width
    qr_height: int # QR code height


class AnswerSheet:
    def __init__(self, list_codes: list[str] | tuple[str], num_questions: int | float,
                 num_options: int | float, filename: str = 'sheet.pdf',
                 fontname: str = 'Times-Roman', fontsize: int | float = 12):
        """
        Initializes an AnswerSheet instance.

        Args:
            list_codes (list[str] | tuple[str]): A list or tuple of unique codes of each applicant.
            num_questions (int | float): The total number of questions in the sheet.
            num_options (int | float): The number of answer options per question.
            filename (str, optional): The name of the output PDF file. Defaults to 'sheet.pdf'.
            fontname (str, optional): The font name used in the PDF. Defaults to 'Times-Roman'.
            fontsize (int | float, optional): The font size used in the PDF. Defaults to 12.

        Raises:
            TypeError: If any argument does not match the expected type.
            ValueError: If `num_questions` or `num_options` is less than 1.
        """

        # list of codes validation
        if not isinstance(list_codes, (list, tuple)):
            raise TypeError(f'List of codes must be a list or tuple, not {type(list_codes).__name__}.')
        
        # number of questions validation
        if not isinstance(num_questions, (int, float)):
            raise TypeError(f'Number of questions must be a int or float, not {type(num_questions).__name__}.')
        if num_questions < 1:
            raise ValueError(f'Numbe rof questions must be greater than 0, received {num_questions}.')
        
        # number of options validation
        if not isinstance(num_options, (int, float)):
            raise TypeError(f'Number of options must be a int or float, not {type(num_options).__name__}.')
        if num_options < 1:
            raise ValueError(f'Number of options must be greater than 0, received {num_options}.')
        
        # filename or path validation
        if not isinstance(filename, str):
            raise TypeError(f'File name or path must be a str, not {type(filename).__name__}.')
        
        # font name validation
        if not isinstance(fontname, str):
            raise TypeError(f'Font name must be a str, not {type(fontname).__name__}.')
        
        # font size validation
        if not isinstance(fontsize, (int, float)):
            raise TypeError(f'Font size must be a int or float, not {type(fontsize).__name__}.')

        self.list_codes = tuple(list_codes)
        self.n_questions = num_questions
        self.n_options = num_options
        self.filename = filename

        self.title: None | str = None
        self._title: bool = False # check if a title is applied

        self.logo: None | str = None
        self._logo: bool = False # chech if a logo is apllied

        self._border: bool = False

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
            spacing_x=None,
            questions_per_column=None,
            max_questions_per_page=None,
            circle_y_offset=None,
        )

        self.config.spacing_x = ((self.config.width - 2 * self.config.margin_x) // 2 + 1 + self.config.fontsize - (self.n_options * (self.config.circle_diameter + self.config.option_spacing))) // 2
        self.config.questions_per_column = int((self.config.height - 2 * self.config.margin_y) // (self.config.spacing_y))
        self.config.max_questions_per_page = 2 * self.config.questions_per_column - 2
        self.config.circle_y_offset = self.config.fontsize - self.config.circle_diameter + 1

    def __str__(self) -> str:
        """
        Return str(self).
        """

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
    title: {f'True, text="{self.title}"' if self._title else 'False'}
    logo: {fr'True, path="{self.logo}"' if self._logo else 'False'}
    border: {self._border}'''
        
        return s

    def __drawTitle__(self) -> None:
        """
        Sets a title at the top center of each sheet. 
        """
        
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
            y=self.config.height - self.config.margin_y - titlesize - 10,
            text=self.title
        )

        self.canvas.setFont(self.config.fontname, self.config.fontsize)

    def __drawLogo__(self) -> None:
        """
        Sets the logo on each page of the PDF.

        If the title is applied, insert the logo at the top left of the page. 
        If not applicable, insert the logo to the left of the QR code.
        """

        if not self._logo:
            return

        if self._title:
            self.canvas.drawImage(
                self.logo, 
                x=self.config.margin_x,
                y=self.config.height - self.config.margin_y - 26 * 2,
                width=26 * 2,
                height=26 * 2
            )
        else:
            self.canvas.drawImage(
                self.logo, 
                x=self.config.width // 2 + self.config.spacing_x,
                y=self.config.margin_y + 26 // 2,
                width=26 * 2,
                height=26 * 2
            )

    def __drawBorder__(self) -> None:
        """
        Sets the page border on each page of the PDF.
        """

        if not self._border:
            return

        self.canvas.drawBoundary(
            sb=0.5, x1=self.config.margin_x, y1=self.config.margin_y,
            width=self.config.width - 2 * self.config.margin_x,
            height=self.config.height - 2 * self.config.margin_y
        )

    def __drawPageFormat__(self) -> None:
        """
        Sets up the page format for the answer sheet.

        This method defines the layout of the page, including margins, title (if applicable), 
        logo (if applicable), and dividing lines. It ensures that each page follows a consistent 
        format before drawing questions and QR codes.
        """

        self.__drawTitle__()
        self.__drawLogo__()

        self.__drawBorder__()

        self.canvas.line(
            x1=self.config.width // 2,
            y1=self.config.margin_y,
            x2=self.config.width // 2,
            y2=self.config.height - self.config.margin_y - (26 * 2 if self._title else 0)
        )

    def __drawQRCode__(self, string: str) -> None:
        """
        Inserts a QR code on the answer sheet.

        This method generates and places a QR code on each page of the PDF. 
        The QR code contains the participant's unique code, the first question 
        number on the page, and the last question number on the page.

        Args:
            string (str): The encoded information to be stored in the QR code.
        """

        buffer = BytesIO()
        create_qr(f'{string}').save(buffer, format="PNG")
        buffer.seek(0)

        self.canvas.drawImage(
            image=ImageReader(buffer),
            x=self.config.width - self.config.margin_x - self.config.qr_width - 2 * self.config.spacing_x,
            y=self.config.margin_y + 26 // 2,
            width=self.config.qr_width,
            height=self.config.qr_height,
        )

    def __drawQuestions__(self, code: str) -> None:
        """
        Draws the questions and answer options on the sheet.

        This method places the question numbers and corresponding answer bubbles 
        on the answer sheet. It also handles pagination, ensuring that the questions 
        are distributed correctly across multiple pages if needed.

        Args:
            code (str): The unique identifier code for the answer sheet.
        """

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
        """
        Draws a new page for the answer sheet.

        This method sets up the format for a new page, including margins, 
        title (if applicable), logo (if applicable), and the question layout. 
        It prepares the canvas for drawing the questions and QR codes.

        Args:
            code (str): The unique identifier code for the answer sheet.
        """

        self.__drawPageFormat__()

        self.canvas.setFont(self.config.fontname, self.config.fontsize)
        self.__drawQuestions__(code)

    def addTitle(self, title: str) -> None:
        """
        Adds a title to the answer sheet (optional).

        This method sets a title to be displayed at the top of the answer sheet. 
        If not called, the answer sheet will be generated without a title.

        Args:
            title (str): The title text to be added to the sheet.
        """

        self.title = title
        self._title = True

        self.config.questions_per_column -= 1
        self.config.max_questions_per_page -= 2

    def addLogo(self, logo_path: str) -> None:
        """
        Adds a logo to the answer sheet (optional).

        This method sets a logo image to be displayed on the answer sheet. 
        If not called, the answer sheet will be generated without a logo.

        Args:
            logo_path (str): The file path of the logo image.
        """

        self.logo = logo_path
        self._logo = True

    def addBorder(self) -> None:
        """
        Adds a page border to the answer sheet (optional).

        The page border is separated by margin_x and margin_y.
        """

        self._border = True

    def generate(self) -> None:
        """
        Generates the answer sheets for all provided codes.

        Iterates through the list of codes and creates a formatted answer sheet 
        for each, adding the necessary elements such as questions, answer options, 
        QR codes, and page formatting.
        """

        for code in self.list_codes:
            self.__drawNewPage__(code)
            self.canvas.showPage()

    def save(self) -> None:
        """
        Saves the generated answer sheet as a PDF file.

        This method finalizes and writes the canvas content to the specified 
        PDF file, making the answer sheet ready for printing or distribution.
        """

        self.canvas.save()