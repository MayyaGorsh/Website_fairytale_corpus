import sys
import pandas as pd
import nltk
import re
from pymorphy2 import MorphAnalyzer
from collections import Counter

nltk.download('punkt')

morphology = MorphAnalyzer()

corpus_data = pd.read_csv("corpus.csv", delimiter=",")

def check_word_form(request_part, row, word_ix):
    # принимает:
    # часть запроса (например, знать),
    # строку df с данными одного предложения
    # номер токена в этой строке, который мы проверяем

    # возвращает: bool, подходит ли этот токен под запрос

    # Лемматизируем запрос
    request_lemma = morphology.parse(request_part.lower())[0].normal_form  # Приводим запрос к нижнему регистру

    word_lemma = row['lemmas'].split(';')[word_ix]

    return request_lemma == word_lemma


def check_exact_form(request_part, row, word_ix):
    # принимает:
    # часть запроса уже без кавычек (например, знает),
    # строку df с данными одного предложения
    # номер токена в этой строке, который мы проверяем

    # возвращает: bool, подходит ли этот токен под запрос

    return request_part.lower() == row['tokens'].split(';')[word_ix].lower()


def check_lemma_and_pos(request_part, row, word_ix):
    # принимает:
    # часть запроса (например, знать+VERB),
    # строку df с данными одного предложения
    # номер токена в этой строке, который мы проверяем

    # возвращает: bool, подходит ли этот токен под запрос

    request = request_part.split('+')
    request_lemma = request[0].lower()
    request_pos = request[1]

    word_lemma = row['lemmas'].split(';')[word_ix]
    word_pos = row['pos_tags'].split(';')[word_ix]

    if request_lemma == word_lemma and request_pos == word_pos:
        return True
    return False


def check_pos(request_part, row, word_ix):
    # принимает:
    # часть запроса (например, VERB),
    # строку df с данными одного предложения
    # номер токена в этой строке, который мы проверяем

    # возвращает: bool, подходит ли этот токен под запрос

    word_pos = row['pos_tags'].split(';')[word_ix]
    return request_part == word_pos


def word_fits_request_part(request_part, row, word_ix):
    # принимает:
    # часть запроса (например, знать+VERB),
    # строку df с данными одного предложения
    # номер токена в этой строке, который мы проверяем

    # возвращает: bool, подходит ли этот токен под запрос

    if '"' in request_part:
        # Запрос точной формы без учетам регистра
        request = request_part.strip('"').lower()
        word_res = check_exact_form(request, row, word_ix)
    elif '+' in request_part:
        # Запрос по лемме и части речи
        word_res = check_lemma_and_pos(request_part, row, word_ix)
    elif all((ord('A') <= ord(ch) <= ord('Z')) for ch in request_part):
        # Запрос по POS тегу - заглавные латинские буквы
        word_res = check_pos(request_part, row, word_ix)
    else:
        # Запрос всех форм слова, игнорируя регистр
        word_res = check_word_form(request_part, row, word_ix)
    return word_res


# Загрузка данных из файла
corpus_data = pd.read_csv("corpus.csv", delimiter=",")


def search(request, corpus_data):
    # принимает:
    # запрос (например, знать+VERB "ничего" "не"),
    # df с данными всех предложений

    # возвращает:
    # список данных всех предложений которые подошли под запрос (формат см выше)

    request_parts = request.split(' ')
    request_length = len(request_parts)
    matching_sentences = []

    for _, row in corpus_data.iterrows():
        tokens = row['tokens'].split(';')
        dirty_tokens = row['sents'].strip().replace('— ', '—').replace('– ', '–').replace(' !', '!').replace(',—',
                                                                                                             ', —').replace(
            ' ,', ',').replace('е.Н', 'е. Н').split(' ')  # для вывода со знаками препинания

        for token_i in range(len(tokens) - request_length + 1):
            phrase_res = True  # Предполагаем, что н-грамма подойдёт
            for j in range(request_length):
                if not word_fits_request_part(request_parts[j], row, token_i + j):
                    phrase_res = False  # Н-грамма не подходит
                    break

            if phrase_res:
                # Нашли подходящую n-грамму!
                phrase_start = token_i  # номер первого токена в этой н-грамме
                phrase_end = token_i + request_length - 1
                collocation = ' '.join(dirty_tokens[phrase_start:phrase_end + 1])  # центральный контекст
                left_cont = ' '.join(dirty_tokens[:phrase_start])  # левый контекст
                right_cont = ' '.join(dirty_tokens[phrase_end + 1:])  # правый контекст
                matching_sentences.append([left_cont, collocation, right_cont, row['name'] + ' ' + row['href']])
            # Переходим к следующему токену
        # Переходим к следующему предложению
    return matching_sentences


def get_collocations(lines):
    # принимает:
    # список данных всех предложений которые подошли под запрос (формат см выше)

    # возвращает:
    # Counter содержащий коллокации
    collocations = Counter()
    for line in lines:
        # Вытаскиваем центр, левый и правый контекст
        center = re.sub(r'[^\w\s-]', '', line[1]).lower()
        left_context = re.sub(r'[^\w\s-]', '', line[0])
        right_context = re.sub(r'[^\w\s-]', '', line[2])
        # Если левый и правый контексты не пустые, то достаем коллокации для левого/правого контекстов
        # После этого записываем их в каунтер
        if left_context != '':
            left = left_context.split()[-1].lower()
            collocation_left = left + ' ' + center
            collocations[collocation_left] += 1
        if right_context != '':
            right = right_context.split()[0].lower()
            collocation_right = center + ' ' + right
            collocations[collocation_right] += 1
            # Сохраняем в список коллокации и их частотность
    return collocations


def pretty_line(c_left='', c_mid='', c_right='', maxlen_l=100, maxlen_m=30, maxlen_r=100, src='?'):
    # принимает - левый, центральный и правый контексты, их максимальные длины и источник
    # возвращает - строку в который все ровненько

    # выравниваем левые контексты по правому краю
    left_part = c_left.rjust(maxlen_l)
    # выравниваем центральный контекст по левому краю
    mid_part = c_mid.ljust(maxlen_m)
    # выравниваем правые контексты по левому краю
    right_part = c_right.ljust(maxlen_r)
    return left_part + ' | ' + mid_part + ' | ' + right_part + ' || Предложение из ' + src


def get_all_pretty_lines(data):
    # принимает - Counter содержащий коллокации
    # возвращает - список, где каждую строку нужно просто напечатать

    # найдем максимальную длину каждого контекста, чтобы выровнять
    maxlen_left = len('Левый контекст')
    maxlen_mid = len('Центральный контекст')
    maxlen_right = len('Правый контекст')
    for line in data:
        maxlen_left = max(maxlen_left, len(line[0]))
        maxlen_mid = max(maxlen_mid, len(line[1]))
        maxlen_right = max(maxlen_right, len(line[2]))

    lines_to_print = []  # результат работы функции
    if not data:
        return lines_to_print
    # внесем шапку
    lines_to_print.append(
        'Левый контекст'.ljust(maxlen_left) + ' | ' + 'Центральный контекст'.ljust(maxlen_mid) + ' | ' +
        'Правый контекст'.ljust(maxlen_right) + ' || ' + 'Источник')
    # внесем примеры
    for line in data:
        lines_to_print.append(pretty_line(line[0], line[1], line[2], maxlen_left, maxlen_mid, maxlen_right, line[3]))
    return lines_to_print


def get_pretty_collocations(data):
    # принимает - список, где каждый элемент -
    # список формата [Левый_контекст, Центральный_контекст, Правый_Контекст, Источник]
    # возвращает - список, где каждую строку нужно просто напечатать

    print_collocations = []  # результат работы функции
    if not data:
        return print_collocations
    maxlen_collocation = len('Коллокация')
    maxlen_frequency = len('Число вхождений')
    for line in data.most_common():
        maxlen_collocation = max(maxlen_collocation, len(line[0]))
        maxlen_frequency = max(maxlen_frequency, len(str(line[1])))
        # внесем шапку
    print_collocations.append(
        'Коллокация'.ljust(maxlen_collocation) + ' | ' + 'Число вхождений'.ljust(maxlen_frequency))
    # внесем примеры
    for line in data.most_common():
        print_collocations.append(line[0].ljust(maxlen_collocation) + ' | ' + str(line[1]).ljust(maxlen_frequency))
    return print_collocations


def main(query=None):
    if not query:
        print('Введите, пожалуйста, ваш запрос:')
        print()
        query = input()  # Если нет аргумента командной строки, использует input()

    examples = search(query, corpus_data)
    if not examples:
        return 'По вашему запросу ничего не найдено'
    else:
        result_lines = ['Вот какие примеры мы нашли по вашему запросу:']
        result_lines.extend(get_all_pretty_lines(examples))
        result_lines.append(' ')
        result_lines.append('А еще у нас получились вот такие коллокации с вот такими частотностями:')
        collocation_frequency = get_collocations(examples)
        pretty_collocations = get_pretty_collocations(collocation_frequency)
        result_lines.extend(pretty_collocations)
        return '\n'.join(result_lines)


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else None
    print(main(query))
