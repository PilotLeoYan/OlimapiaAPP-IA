from dataclasses import dataclass


@dataclass
class SheetConfig:
    """Configuration for the question and answer sheet in the PDF."""

    width: float  # Sheet width
    height: float  # Sheet height
    margin_x: int # Horizontal margin
    margin_y: int # Vertical margin
    fontname: str # Font name
    fontsize: int # Font size
    spacing_x: float # Horizontal space between answer and sheet
    spacing_y: float # Vertical space between each answer
    circle_diameter: int # Circle diameter or Burble diameter
    circle_y_offset: int # Vertical offset of the burble (correction)
    option_spacing: int # Space between each burble
    questions_per_column: int # Maximun of questions per column
    max_questions_per_page: int # Maximum questions per page
    qr_width: int # QR code width
    qr_height: int # QR code height