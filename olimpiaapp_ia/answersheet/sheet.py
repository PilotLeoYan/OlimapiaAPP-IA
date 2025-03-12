from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class AnswerSheet:
    def __init__(self, num_questions: int, num_options: int, filename: str):
        """
        docstring
        """

        # num_questions validation
        if not isinstance(num_questions, int):
            raise TypeError(f"Number of questions must be an integer, not a {type(num_questions).__name__}.")
        if num_questions < 1:
            raise ValueError("Number of questions must be greater than 0.")
        
        # num_options validation
        if not isinstance(num_options, int):
            raise TypeError(f"Number of options must be an integer, not a {type(num_options).__name__}.")
        if num_options < 1:
            raise Exception("Number of options must be greater than 0.")
        
        # filename validation
        if not isinstance(filename, str):
            raise ValueError(f"filename is must be a string, not a {type(filename).__name__}.")
        
        self.num_questions = num_questions
        self.num_options = num_options
        self.filename = filename
        self.canvas = None

    def __str__(self) -> str:
        return fr"AnswerSheet: {self.num_questions} number of questions, {self.num_options} number of questions"

    def generate(self) -> None:
        """
        docstring
        """

        self.canvas = canvas.Canvas(self.filename, pagesize=letter)

        width, height = letter
        margin_x = 60 
        margin_y = 80
        circle_diameter = 14
        spacing_x = 40
        spacing_y = 22
        column_split = 30
        column_gap = 300

        self.canvas.setFont("Helvetica", 12)
        for i in range(self.num_questions):
            column_offset = 0 if i < column_split else column_gap
            y_pos = height - margin_y - ((i % column_split) * spacing_y)
            self.canvas.drawString(margin_x + column_offset - 10, y_pos - 5, f"{i+1}")
            
            for j in range(self.num_options):
                x_pos = margin_x + 30 + (j * spacing_x) + column_offset
                self.canvas.circle(x_pos, y_pos, circle_diameter / 2)
                self.canvas.setFont("Helvetica", 10)
                self.canvas.drawCentredString(x_pos, y_pos - 4, chr(65 + j))

    def save(self) -> None:
        """
        docstring
        """
        if self.canvas is None: # if it is a None
            raise Exception("Execute .generate() before save().")
        self.canvas.save()