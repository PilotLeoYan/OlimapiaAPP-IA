from answersheet import AnswerSheet


def main() -> None:
    sheet = AnswerSheet(
        list_codes=['juan', 'juan_2'],
        num_questions=30,
        num_options=5,
        filename='test1.pdf'
    )

    sheet.generate()
    sheet.save()


if __name__ == '__main__':
    main()