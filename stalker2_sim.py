#!/usr/bin/env python3

"""
Скрипт для моделювання продажів гри за різними джерелами даних і країнами.
Використовує бібліотеку Rich для форматованого виведення таблиць.
"""

import random
from statistics import median

from rich import box
from rich.console import Console
from rich.table import Table

def units_format(num):
    """
    Форматує число з додаванням суфіксів (k, M, G тощо) для скорочення.

    Параметри:
    num (float): число для форматування

    Повертає:
    str: відформатоване число зі скороченням
    """
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.3f %s' % (num, ['', 'k', 'M', 'G', 'T', 'P'][magnitude])

def currency_format(amount: int, sign='$', length=11):
    """
    Форматує суму до заданої довжини з валютою.

    Параметри:
    amount (int): сума грошей для форматування
    sign (str): символ валюти (за замовчуванням "$")
    length (int): довжина поля для форматованої суми (за замовчуванням 15)

    Повертає:
    str: відформатована строка з сумою
    """
    fmt = ' {:>' + str(length) + ',.0f}'
    return sign + fmt.format(amount)

# Джерело: https://steamcommunity.com/groups/steamworks/announcements/detail/1697191267930157838
def steam_fee(revenue: float) -> float:
    """
    Розраховує розмір комісії Steam залежно від загального доходу.

    Параметри:
    revenue (float): загальний дохід у гривнях

    Повертає:
    float: частка комісії Steam
    """
    if revenue / EXCHANGE < 10 * MILLION:
        return 0.3  # 30% комісія для доходів менше $10M
    if revenue / EXCHANGE < 50 * MILLION:
        return 0.25  # 25% комісія для доходів між $10M і $50M
    return 0.2  # 20% комісія для доходів понад $50M

class SalesSimulator:
    """
    Клас для симуляції продажів гри за країнами.

    Атрибути:
    total_sales (int): загальна кількість проданих копій
    sales_by_country (list[tuple[str, float, float]]): дані про частку продажів, ціну за країнами

    Методи:
    simulate_sales(chunk_size=1000): симулює продажі з розрахунком доходу
    """

    def __init__(self, title: str, total_sales: int, sales_by_country: list[tuple[str, float, float]]):
        """
        Ініціалізує симуляцію продажів для заданої гри.

        Параметри:
        title (str): назва гри
        total_sales (int): загальна кількість копій для симуляції
        sales_by_country (list[tuple[str, float, float]]): частки та ціни продажів за країнами
        """
        self.title = title
        self.total_sales = total_sales
        self.sales_by_country = sales_by_country

        self.weights = [share for _, share, _ in sales_by_country]
        self.prices = [price for _, _, price in sales_by_country]

        if sum(self.weights) != 1.0:
            raise ValueError('Сума часток продажів повинна дорівнювати 1')

    def simulate_sales(self, chunk_size=1000):
        """
        Симулює продажі гри та розраховує дохід.

        Параметри:
        chunk_size (int): розмір блоку продажів для моделювання

        Повертає:
        float: загальний дохід у гривнях
        """
        revenue = 0.0

        with console.status("[bold orange3]Симуляція продажів ...", spinner='dots2') as status:
            for i in range(int(self.total_sales / chunk_size)):
                for sale in random.choices(self.prices, self.weights, k=chunk_size):
                    revenue += sale * (1 - steam_fee(revenue))

        return revenue

def calculate_profit(
        estimates: list[tuple[str, int]],
        sales: list[tuple[str, float, float]],
        budget: list[tuple[str, int]]
):
    """
    Розраховує та виводить прибуток за оцінками кількості користувачів.

    Параметри:
    estimates (list[tuple[str, int]]): джерела оцінок та кількість користувачів
    sales (list[tuple[str, float, float]]): дані про продажі (країна, частка, ціна)
    budget (list[tuple[str, int]]): оцінки б'юджету гри
    """
    sim_table = Table(title='[bold bright_white]Stalker 2[/] розрахунок прибутку',
                  caption='* комісія Steam враховано в розрахунок',
                  caption_justify='left',
                  box=box.ROUNDED,
                  )

    sim_table.add_column('[bright_yellow]Джерело[/]', justify='right', style='orange3')
    sim_table.add_column('[bright_yellow]Продані копії[/]', justify='right', style='magenta')
    sim_table.add_column('[bright_yellow]Продажі[/] [turquoise2](UAH)[/]', justify='center', style='green', width=20)
    sim_table.add_column('[bright_yellow]Продажі[/] [turquoise2](USD)[/]', justify='center', style='bright_green', width=20)

    estimates.sort(key=lambda e: e[1])

    for source, units in estimates:
        sales_sim = SalesSimulator(source, units, sales)
        revenue_uah = sales_sim.simulate_sales()

        profit_uah = int(revenue_uah)
        profit_usd = int(revenue_uah / EXCHANGE)

        # Вивід результатів
        sim_table.add_row(
            source,
            f'{units_format(units)}',
            currency_format(profit_uah, sign='₴'),
            currency_format(profit_usd, sign='$')
        )

    sim_table.add_section()

    # Статистичні розрахунки
    units_sold = [units for _, units in estimates]
    for source, units in [
        ('Мінімум', min(units_sold)),
        ('Медіана', median(units_sold)),
        ('Максимум', max(units_sold)),
    ]:
        sales_sim = SalesSimulator(source, units, sales)
        revenue_uah = sales_sim.simulate_sales()

        profit_uah = int(revenue_uah)
        profit_usd = int(revenue_uah / EXCHANGE)

        # Вивід результатів
        sim_table.add_row(
            f'[i bold]{source}[/]',
            f'[i bold]{units_format(units)}[/]',
            f'[i bold]{currency_format(profit_uah, sign="₴")}[/]',
            f'[i bold]{currency_format(profit_usd, sign="$")}[/]'
        )

    console.print(sim_table)

    budget_table = Table(box=box.HORIZONTALS)

    budget_table.add_column('[bold bright_white]Stalker 2[/]', justify='right', style='orange3', width=21)
    budget_table.add_column('[bright_yellow]Б\'юджет[/]', justify='right', style='bright_green', width=50)

    for source, estimate_usd in budget:
        budget_table.add_row(
            f'[i bold]{source}[/]',
            f'[i bold]{currency_format(estimate_usd, sign="$")}[/]'
        )

    console.print(budget_table)

if __name__ == "__main__":
    console = Console()
    MILLION = 1000000

    # Дані про продажі за країнами
    # Джерело: https://vginsights.com/game/s-t-a-l-k-e-r-2-heart-of-chornobyl
    # Джерело: https://x.com/VG_Insights/status/1861015666263752993
    SALES_BY_COUNTRY = [
        ('US', 0.229, 2490.52),
        ('Ukraine', 0.146, 1399.00),
        ('Germany', 0.081, 2634.46),
        ('China', 0.081, 1536.40),
        ('World', 0.463, 1399.00 * 1.5),
    ]

    # Джерело: https://steamdb.info/app/1643320/charts/
    REVIEWS_P = 72521
    REVIEWS_N = 14334

    ESTIMATES_BY_TRACKERS = [
        ('PlayTracker', int(0.814 * MILLION)),
        ('Gamalytic', int(1.30 * MILLION)),
        ('SteamSpy', int(2.31 * MILLION)),
        ('VG Insights', int(2.65 * MILLION)),
        ('відгуки x 20', int(20 * (REVIEWS_N + REVIEWS_P))),
        ('відгуки x 30', int(30 * (REVIEWS_N + REVIEWS_P))),
        ('відгуки x 55', int(55 * (REVIEWS_N + REVIEWS_P))),
    ]

    BUDGET = [
        ('Мінімальний б\'юджет', 30 * MILLION),
        ('Середній б\'юджет', 60 * MILLION),
        ('Максимальний б\'юджет', 100 * MILLION),
    ]

    EXCHANGE = 41.59

    # Розрахунок прибутків для заданих оцінок і продажів
    console.print('[bold bright_white]Stalker 2[/] розрахунок прибутку по інформації з різних джерел')
    console.print(f'* відгуки [blue]{REVIEWS_P + REVIEWS_N}[/] ~ позитивні [green]{REVIEWS_P}[/] + негативні [red]{REVIEWS_N}[/]')
    calculate_profit(ESTIMATES_BY_TRACKERS, SALES_BY_COUNTRY, BUDGET)
