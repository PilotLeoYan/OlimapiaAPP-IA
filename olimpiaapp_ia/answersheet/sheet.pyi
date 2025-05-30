class AnswerSheet:
    def __init__(
        self, list_codes: list[str] | tuple[str],
        num_questions: int,
            num_options: int, 
            filename: str = 'sheet.pdf',
            fontname: str = 'Times-Roman', 
            fontsize: int | float = 12
        ) -> None:
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
        ...

    def __str__(self) -> str:
        """Return str(self)."""
        ...

    def __drawTitle__(self) -> None:
        """Set a title at the top center of each sheet."""
        ...

    def __drawLogo__(self) -> None:
        """
        Set the logo on each page of the PDF.

        If the title is applied, insert the logo at the top left of the page. 
        If not applicable, insert the logo to the left of the QR code.
        """
        ...

    def __drawBorder__(self) -> None:
        """Set the page border on each page of the PDF."""
        ...

    def __drawVerticalLine__(self) -> None:
        """Set a vertical line in the middle on each page of the PDF."""
        ...

    def __drawNumeration__(self) -> None:
        """Set a page number in each answer sheet."""
        ...

    def __drawPageFormat__(self) -> None:
        """
        Set up the page format for the answer sheet.

        This method defines the layout of the page, including margins, title (if applicable), 
        logo (if applicable), and dividing lines. It ensures that each page follows a consistent 
        format before drawing questions and QR codes.
        """
        ...

    def __drawQRCode__(self, string: str) -> None:
        """
        Insert a QR code on the answer sheet.

        This method generates and places a QR code on each page of the PDF. 
        The QR code contains the participant's unique code, the first question 
        number on the page, and the last question number on the page.

        Args:
            string (str): The encoded information to be stored in the QR code.
        """
        ...

    def __drawQuestions__(self, code: str) -> None:
        """
        Draw the questions and answer options on the sheet.

        This method places the question numbers and corresponding answer bubbles 
        on the answer sheet. It also handles pagination, ensuring that the questions 
        are distributed correctly across multiple pages if needed.

        Args:
            code (str): The unique identifier code for the answer sheet.
        """
        ...

    def __drawNewPage__(self, code: str) -> None:
        """
        Draw a new page for the answer sheet.

        This method sets up the format for a new page, including margins, 
        title (if applicable), logo (if applicable), and the question layout. 
        It prepares the canvas for drawing the questions and QR codes.

        Args:
            code (str): The unique identifier code for the answer sheet.
        """
        ...

    @property
    def title(self) -> str | None:
        """Return the title of the answer sheet"""
        ...

    @title.setter
    def title(self, title: str) -> None:
        """
        Set a title to the answer sheet (optional).

        This method sets a title to be displayed at the top of the answer sheet. 
        If not called, the answer sheet will be generated without a title.

        Args:
            title (str): The title text to be added to the sheet.
        """
        ...

    @property
    def logo(self) -> None | str:
        """Return the path of the logo."""

    @logo.setter
    def logo(self, logo_path: str) -> None:
        """
        Add a logo to the answer sheet (optional).

        This method sets a logo image to be displayed on the answer sheet. 
        If not called, the answer sheet will be generated without a logo.

        Args:
            logo_path (str): The file path of the logo image.
        """
        ...

    def border(self) -> None:
        """
        Add a page border to the answer sheet (optional).

        The page border is separated by margin_x and margin_y.
        """
        ...

    def verticalLine(self) -> None:
        """Add a vertical line down the center of the Answer Sheet (optional)."""
        ...

    def numeration(self, start: int = 1) -> None:
        """
        Add page numbering to all pages with an increment of one (optional).

        Args:
            start (int): first number for numering (optional).
        """
        ...

    def generate(self) -> None:
        """
        Generates the answer sheets for all provided codes.

        Iterates through the list of codes and creates a formatted answer sheet 
        for each, adding the necessary elements such as questions, answer options, 
        QR codes, and page formatting.
        """
        ...

    def save(self) -> None:
        """
        Saves the generated answer sheet as a PDF file.

        This method finalizes and writes the canvas content to the specified 
        PDF file, making the answer sheet ready for printing or distribution.
        """
        ...