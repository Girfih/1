#!/usr/bin/env python3
"""Набор консольных мини-игр: карты, рулетка, 21 и другие."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class PlayerState:
    name: str
    chips: int = 100

    def can_bet(self, amount: int) -> bool:
        return 0 < amount <= self.chips


def ask_int(prompt: str, minimum: int | None = None, maximum: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Введите число.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Нужно целое число.")
            continue
        if minimum is not None and value < minimum:
            print(f"Число должно быть не меньше {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Число должно быть не больше {maximum}.")
            continue
        return value


def ask_bet(player: PlayerState) -> int:
    while True:
        amount = ask_int(f"Ставка (1..{player.chips}): ", minimum=1, maximum=player.chips)
        if player.can_bet(amount):
            return amount
        print("Некорректная ставка.")


def game_high_card(player: PlayerState) -> None:
    """Карточная игра: у кого выше карта."""
    print("\n=== Карты: старшая карта ===")
    bet = ask_bet(player)
    ranks = list(range(2, 15))
    suits = ["♠", "♥", "♦", "♣"]

    player_card = (random.choice(ranks), random.choice(suits))
    dealer_card = (random.choice(ranks), random.choice(suits))

    names = {11: "Валет", 12: "Дама", 13: "Король", 14: "Туз"}

    def card_str(card: tuple[int, str]) -> str:
        rank, suit = card
        rank_text = names.get(rank, str(rank))
        return f"{rank_text}{suit}"

    print(f"Ваша карта: {card_str(player_card)}")
    print(f"Карта дилера: {card_str(dealer_card)}")

    if player_card[0] > dealer_card[0]:
        player.chips += bet
        print(f"Победа! +{bet} фишек.")
    elif player_card[0] < dealer_card[0]:
        player.chips -= bet
        print(f"Проигрыш! -{bet} фишек.")
    else:
        print("Ничья. Ставка возвращена.")


def game_roulette(player: PlayerState) -> None:
    """Упрощённая рулетка: ставка на цвет или точное число."""
    print("\n=== Рулетка ===")
    bet = ask_bet(player)
    print("1) Цвет (красное/чёрное) x2")
    print("2) Точное число (0..36) x36")
    choice = ask_int("Выберите тип ставки: ", minimum=1, maximum=2)

    spin = random.randint(0, 36)
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

    if spin == 0:
        spin_color = "зелёное"
    elif spin in red_numbers:
        spin_color = "красное"
    else:
        spin_color = "чёрное"

    if choice == 1:
        color_choice = input("Введите цвет (красное/чёрное): ").strip().lower()
        if color_choice not in {"красное", "чёрное"}:
            print("Некорректный цвет, ставка считается проигранной.")
            player.chips -= bet
        elif color_choice == spin_color:
            player.chips += bet
            print(f"Выпало {spin} ({spin_color}). Победа! +{bet} фишек.")
        else:
            player.chips -= bet
            print(f"Выпало {spin} ({spin_color}). Проигрыш! -{bet} фишек.")
    else:
        number = ask_int("Введите число (0..36): ", minimum=0, maximum=36)
        if number == spin:
            win = bet * 35
            player.chips += win
            print(f"Выпало {spin}. Джекпот! +{win} фишек.")
        else:
            player.chips -= bet
            print(f"Выпало {spin}. Проигрыш! -{bet} фишек.")


def hand_value(cards: list[int]) -> int:
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def draw_card() -> int:
    ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    return random.choice(ranks)


def game_blackjack(player: PlayerState) -> None:
    """Игра 21 (Blackjack)."""
    print("\n=== 21 (Blackjack) ===")
    bet = ask_bet(player)

    player_cards = [draw_card(), draw_card()]
    dealer_cards = [draw_card(), draw_card()]

    while True:
        print(f"Ваши карты: {player_cards} (сумма: {hand_value(player_cards)})")
        print(f"Карта дилера: {dealer_cards[0]} и [?]")

        if hand_value(player_cards) >= 21:
            break

        action = input("Взять карту? (д/н): ").strip().lower()
        if action == "д":
            player_cards.append(draw_card())
        else:
            break

    player_score = hand_value(player_cards)
    if player_score > 21:
        player.chips -= bet
        print(f"Перебор ({player_score}). Проигрыш! -{bet} фишек.")
        return

    while hand_value(dealer_cards) < 17:
        dealer_cards.append(draw_card())

    dealer_score = hand_value(dealer_cards)
    print(f"Карты дилера: {dealer_cards} (сумма: {dealer_score})")

    if dealer_score > 21 or player_score > dealer_score:
        player.chips += bet
        print(f"Победа! +{bet} фишек.")
    elif player_score < dealer_score:
        player.chips -= bet
        print(f"Проигрыш! -{bet} фишек.")
    else:
        print("Ничья. Ставка возвращена.")


def game_guess_number(player: PlayerState) -> None:
    """Угадай число за ограниченное количество попыток."""
    print("\n=== Угадай число ===")
    bet = ask_bet(player)
    secret = random.randint(1, 20)
    attempts = 5

    for turn in range(1, attempts + 1):
        guess = ask_int(f"Попытка {turn}/{attempts}. Ваше число (1..20): ", minimum=1, maximum=20)
        if guess == secret:
            win = bet * 2
            player.chips += win
            print(f"Точно! Вы угадали и получили +{win} фишек.")
            return
        hint = "больше" if guess < secret else "меньше"
        print(f"Не угадали. Загаданное число {hint}.")

    player.chips -= bet
    print(f"Попытки закончились. Было число {secret}. -{bet} фишек.")


def game_rock_paper_scissors(player: PlayerState) -> None:
    """Камень-ножницы-бумага с одной ставкой."""
    print("\n=== Камень-ножницы-бумага ===")
    bet = ask_bet(player)

    options = {"к": "камень", "н": "ножницы", "б": "бумага"}
    user = input("Ваш выбор: (к)амень, (н)ожницы, (б)умага: ").strip().lower()
    if user not in options:
        print("Неверный выбор, ставка проиграна.")
        player.chips -= bet
        return

    bot = random.choice(list(options))
    user_name = options[user]
    bot_name = options[bot]
    print(f"Вы: {user_name}, компьютер: {bot_name}")

    wins = {("к", "н"), ("н", "б"), ("б", "к")}
    if user == bot:
        print("Ничья.")
    elif (user, bot) in wins:
        player.chips += bet
        print(f"Победа! +{bet} фишек.")
    else:
        player.chips -= bet
        print(f"Проигрыш! -{bet} фишек.")


def main() -> None:
    print("Добро пожаловать в набор Python-игр! 🎮")
    name = input("Ваше имя: ").strip() or "Игрок"
    player = PlayerState(name=name)

    games = {
        1: ("Карты: старшая карта", game_high_card),
        2: ("Рулетка", game_roulette),
        3: ("21 (Blackjack)", game_blackjack),
        4: ("Угадай число", game_guess_number),
        5: ("Камень-ножницы-бумага", game_rock_paper_scissors),
    }

    while True:
        print("\n" + "=" * 40)
        print(f"Игрок: {player.name} | Фишки: {player.chips}")
        print("Выберите игру:")
        for num, (title, _) in games.items():
            print(f"{num}) {title}")
        print("0) Выход")

        choice = ask_int("Ваш выбор: ", minimum=0, maximum=len(games))
        if choice == 0:
            print(f"Спасибо за игру, {player.name}! Осталось фишек: {player.chips}")
            return

        _, game_fn = games[choice]
        game_fn(player)

        if player.chips <= 0:
            print("Фишки закончились. Игра окончена!")
            return


if __name__ == "__main__":
    main()
