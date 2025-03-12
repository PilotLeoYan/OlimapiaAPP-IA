from answersheet import AnswerSheet


def main() -> None:
    sheet = AnswerSheet(
        50,
        5,
        'test1.pdf'
    )

    sheet.generate()
    sheet.save()


if __name__ == '__main__':
    main()