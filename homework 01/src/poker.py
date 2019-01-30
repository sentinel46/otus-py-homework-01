#!/usr/bin/python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools
# Можно свободно определять свои функции и т.п.
# -----------------

from itertools import permutations


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    rank_dict = {'2': 2,
                 '3': 3,
                 '4': 4,
                 '5': 5,
                 '6': 6,
                 '7': 7,
                 '8': 8,
                 '9': 9,
                 'T': 10,
                 'J': 11,
                 'Q': 12,
                 'K': 13,
                 'A': 14}
    ranks = [rank_dict[card[0]] for card in hand]
    ranks.sort(reverse=True)
    return ranks


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    first_suit = hand[0][1]
    return all(first_suit == card[1] for card in hand[1:])


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return all(ranks[i+1] == ranks[i] - 1 for i in range(0, len(ranks)-1))


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    return max([rank for rank in set(ranks) if ranks.count(rank) == n], default=None)


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    good_ranks = [rank for rank in set(ranks) if ranks.count(rank) == 2]
    return good_ranks[::-1] if len(good_ranks) == 2 else None


def compare_ranks(rank1, rank2):
    if rank1[0] > rank2[0]:
        return True
    elif rank1[0] < rank2[0]:
        return False
    else:
        rank1_info = rank1[1:]
        rank2_info = rank2[1:]
        for i in range(0, min(len(rank1_info), len(rank2_info))):
            if rank1_info[i] > rank2_info[i]:
                return True
            elif rank1_info[i] < rank2_info[i]:
                return False
    return True


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    result_hand = []
    result_rank = (0, [])
    for sub_hand in permutations(hand, 5):
        if compare_ranks(hand_rank(sub_hand), result_rank):
            result_hand = sub_hand
            result_rank = hand_rank(sub_hand)
    return result_hand


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    black_cards = ["2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC",
                   "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS"]
    red_cards = ["2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
                 "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH"]
    result_hand = []
    result_rank = (0, [])
    if "?B" in hand:
        black_joker_index = hand.index("?B")
        for black_card in black_cards:
            if black_card not in hand:
                hand[black_joker_index] = black_card
                for sub_hand in permutations(hand, 5):
                    if compare_ranks(hand_rank(sub_hand), result_rank):
                        result_hand = sub_hand
                        result_rank = hand_rank(sub_hand)
    return result_hand


def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_best_hand()
#    print(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))

    test_best_wild_hand()
