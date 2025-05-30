from answersheet import AnswerSheet


sheet = AnswerSheet(
    list_codes=['juan1', 'pepe'],
    num_questions=30,
    num_options=5,
)

# optional 
sheet.title = 'Release v1.0.0' 
sheet.logo = r'./logo.png'
sheet.border()
sheet.verticalLine()
sheet.numeration()

print(sheet)

# generate and save
sheet.generate()
sheet.save()
