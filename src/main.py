from utils import HeadHunter, SuperJob, Connector


def main():
    vacancies_json = []
    keyword = input("Введите профессию или должность: ")

    hh = HeadHunter(keyword)
    sj = SuperJob(keyword)
    for api in (hh, sj):
        api.get_vacancies(pages_count=10)
        vacancies_json.extend(api.get_formatted_vacancies())

        connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

        while True:
            command = input(
                '1 - Вывести список вакансий;\n'
                '2 - Отсортировать по возврастанию дохода;\n'
                '3 - Отсортировать по убыванию дохода;\n'
                '0 - Выход;\n'
            )
            if command.lower() == "0":
                break
            elif command == "1":
                vacancies = connector.select()
            elif command == "2":
                vacancies = connector.sorted_vacancies_by_salary_from_asc()
            elif command == "3":
                vacancies = connector.sorted_vacancies_by_salary_to_asc()
            else:
                print("Не корректные данные")
                exit()

            for vacancy in vacancies:
                print(vacancy, end="\n\n")


if __name__ == "__main__":
    main()