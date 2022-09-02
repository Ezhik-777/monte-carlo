from re import A
import time
import argparse
import numpy as np
from scipy.stats import norm
from joblib import Parallel, delayed

UOM = '€'

parser = argparse.ArgumentParser(description='monte-carlo калькулятор')
parser.add_argument("-f", "--first_deposit", required=True, type=int, help="Первый взнос")
parser.add_argument("-m", "--monthly_deposit", required=True, type=int, help="Ежемесячный взнос")
parser.add_argument("-%", "--interest_rate", required=True, type=float, help="Процентная ставка")
parser.add_argument("-v", "--volatility", required=True, type=int, help="Волатильность")
parser.add_argument("-d", "--dynamic", required=True, type=int, help="Динамика")
parser.add_argument("-y", "--years_number", required=True, type=int, help="Срок инвестирования (лет)")
parser.add_argument("-i", "--iter_number", required=True, type=int, help="Количество итераций")

args = parser.parse_args()

def calc_ending_value(monthly_deposit, interest_rate, volatility, dynamic, ending_value):

    # раскомментировать для повторяемости получаемых результатов при каждом запуске программы
    # (оставил для проверки, раскомментировать не нужно)
    # np.random.seed(33)

    norm_obr = interest_rate

    if volatility > 0:
        '''
        Ф-ция НОРМ.ОБР Excel - возвращает обратное кумулятивному распределению CFD
        PPF - квантиль-функция расчета обратного нормального распределения
        '''
        norm_obr = norm.ppf(np.random.random(), interest_rate, volatility)

    return ending_value * (1 + norm_obr) + (12. * monthly_deposit * (1 + dynamic))


def calc_last_ending_value(first_deposit, monthly_deposit, interest_rate, volatility, dynamic, years_number):
    ending_value = first_deposit
    for i in range(0, years_number):
        ending_value = calc_ending_value(monthly_deposit, interest_rate, volatility, dynamic, ending_value)
    # print(f'[debug] Сумма через {years_number} лет (0-я итерация Монте-Карло): {ending_value:,.0f} {UOM}')
    return ending_value


def calc(first_deposit, monthly_deposit, interest_rate, volatility, dynamic, years_number, iter_number, *percentiles):

    print()
    print('[+] Исходные данные:')
    print(f'Первый взнос: {first_deposit:,.2f} {UOM}')
    print(f'Ежемесячный взнос: {monthly_deposit:,.2f} {UOM}')
    print(f'Процентная ставка: {100. * interest_rate}%')
    print(f'Волатильность: {100. * volatility}%')
    print(f'Динамика: {100. * dynamic}%')
    print(f'Срок инвестирования: {years_number} лет')
    print(f'Количество итераций метода Монте-Карло: {iter_number}')
    print()

    # нулевая волатильность
    novolatility_value = calc_last_ending_value(first_deposit, monthly_deposit, interest_rate, 0, dynamic, years_number)

    # метод Монте-Карло
    ending_values = Parallel(n_jobs=32)(delayed(calc_last_ending_value)(first_deposit, monthly_deposit, interest_rate, volatility, dynamic, years_number) for i in range(iter_number))

    mean = np.mean(ending_values)
    median = np.median(ending_values)
    percentile_vals = np.percentile(ending_values, percentiles)

    return novolatility_value, mean, median, percentile_vals


if __name__ == '__main__':
    start_time = time.time()

first_deposit = args.first_deposit
monthly_deposit = args.monthly_deposit
interest_rate = args.interest_rate
interest_rate = interest_rate / 100
volatility = args.volatility
volatility = volatility / 100
dynamic = args.dynamic
dynamic = dynamic / 100
years_number = args.years_number
iter_number = args.iter_number


percentiles = [99, 95, 75, 25, 5, 1]
novolatility_value, mean, median, percentile_vals = calc(first_deposit, monthly_deposit, interest_rate, volatility, dynamic, years_number, iter_number, percentiles)

print(f'[+] Нулевая волатильность: ')
print(f'Значение: {novolatility_value:,.0f} {UOM}')
print()
print('[+] Метод Монте-Карло:')
print(f'Среднее значение: {mean:,.0f} {UOM}')
print(f'Медиана: {median:,.0f} {UOM}')
for i, perc in enumerate(percentile_vals[0]):
    print(f'Процентиль {percentiles[i]}%: {perc:,.0f} {UOM}')
print()

print("Время счета: %s секунд" % (time.time() - start_time))
