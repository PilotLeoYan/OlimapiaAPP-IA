from answersheet import AnswerSheet


def main() -> None:
    sheet = AnswerSheet(
        ['juan'],
        32 * 2 + 1,
        5
    )

    sheet.addTitle('Titulo aqui')
    sheet.addLogo(r'./logo.png')
    #sheet.addBorder()
    #sheet.addVerticalLine()

    print(sheet)

    sheet.generate()
    sheet.save()


if __name__ == '__main__':
    main()