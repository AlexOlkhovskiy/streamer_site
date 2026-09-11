from datetime import datetime


months_list = [
    "Апрель 2025",
    "Июнь 2022",
    "Январь 2025",
    "Май 2023",
    "Январь 2024",
]

month_map = {
    "Январь": 1,
    "Февраль": 2,
    "Март": 3,
    "Апрель": 4,
    "Май": 5,
    "Июнь": 6,
    "Июль": 7,
    "Август": 8,
    "Сентябрь": 9,
    "Октябрь": 10,
    "Ноябрь": 11,
    "Декабрь": 12
}

sorted_months = sorted(
    months_list,
    key=lambda x: (-int(x.split()[1]), month_map[x.split()[0]])
)

print(sorted_months)
