from answersheet import AnswerSheet


sheet = AnswerSheet(
    list_codes=['juan1', 'pepe'],
    num_questions=30,
    num_options=5,
)

sheet.addTitle('Release v1.0.0')
sheet.addLogo(r'./logo.png')
#sheet.addBorder()
#sheet.addVerticalLine()

print(sheet)

sheet.generate()
sheet.save()
