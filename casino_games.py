#!/usr/bin/env python3
"""GUI-набор мини-игр: карты, рулетка, 21 и другие."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk


RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
CARD_RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
CARD_NAMES = {11: "Валет", 12: "Дама", 13: "Король", 14: "Туз"}
SUITS = ["♠", "♥", "♦", "♣"]
RPS_OPTIONS = ["камень", "ножницы", "бумага"]


@dataclass
class PlayerState:
    name: str
    chips: int = 200
    games_played: int = 0
    wins: int = 0

    def can_bet(self, amount: int) -> bool:
        return 0 < amount <= self.chips

    def register_result(self, won: bool) -> None:
        self.games_played += 1
        if won:
            self.wins += 1


@dataclass
class GameResult:
    delta: int
    message: str
    won: bool


def parse_bet(player: PlayerState, raw_bet: str) -> int:
    try:
        bet = int(raw_bet)
    except ValueError as exc:
        raise ValueError("Ставка должна быть целым числом.") from exc
    if not player.can_bet(bet):
        raise ValueError(f"Ставка должна быть в диапазоне 1..{player.chips}.")
    return bet


def update_balance(player: PlayerState, result: GameResult) -> None:
    player.chips += result.delta
    player.register_result(result.won)


def draw_card_rank() -> int:
    return random.choice(list(range(2, 15)))


def card_to_text(rank: int, suit: str) -> str:
    return f"{CARD_NAMES.get(rank, rank)}{suit}"


def play_high_card(player: PlayerState, bet: int) -> GameResult:
    user = (draw_card_rank(), random.choice(SUITS))
    dealer = (draw_card_rank(), random.choice(SUITS))

    if user[0] > dealer[0]:
        return GameResult(
            delta=bet,
            won=True,
            message=f"Ваша карта: {card_to_text(*user)}\nКарта дилера: {card_to_text(*dealer)}\nПобеда! +{bet} фишек.",
        )
    if user[0] < dealer[0]:
        return GameResult(
            delta=-bet,
            won=False,
            message=f"Ваша карта: {card_to_text(*user)}\nКарта дилера: {card_to_text(*dealer)}\nПроигрыш! -{bet} фишек.",
        )
    return GameResult(
        delta=0,
        won=False,
        message=f"Ваша карта: {card_to_text(*user)}\nКарта дилера: {card_to_text(*dealer)}\nНичья, ставка возвращена.",
    )


def roulette_color(num: int) -> str:
    if num == 0:
        return "зелёное"
    if num in RED_NUMBERS:
        return "красное"
    return "чёрное"


def play_roulette_color(bet: int, color_choice: str) -> GameResult:
    spin = random.randint(0, 36)
    color = roulette_color(spin)
    if color_choice == color:
        return GameResult(delta=bet, won=True, message=f"Выпало {spin} ({color}). Победа +{bet}.")
    return GameResult(delta=-bet, won=False, message=f"Выпало {spin} ({color}). Проигрыш -{bet}.")


def play_roulette_number(bet: int, number: int) -> GameResult:
    spin = random.randint(0, 36)
    if number == spin:
        win = bet * 35
        return GameResult(delta=win, won=True, message=f"Выпало {spin}. Джекпот! +{win}.")
    return GameResult(delta=-bet, won=False, message=f"Выпало {spin}. Проигрыш -{bet}.")


def hand_value(cards: list[int]) -> int:
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def draw_blackjack_card() -> int:
    return random.choice(CARD_RANKS)


def play_blackjack(bet: int) -> GameResult:
    user_cards = [draw_blackjack_card(), draw_blackjack_card()]
    dealer_cards = [draw_blackjack_card(), draw_blackjack_card()]

    while hand_value(user_cards) < 17:
        user_cards.append(draw_blackjack_card())

    user_score = hand_value(user_cards)
    if user_score > 21:
        return GameResult(
            delta=-bet,
            won=False,
            message=f"Ваши карты: {user_cards} ({user_score})\nПеребор. -{bet}",
        )

    while hand_value(dealer_cards) < 17:
        dealer_cards.append(draw_blackjack_card())
    dealer_score = hand_value(dealer_cards)

    if dealer_score > 21 or user_score > dealer_score:
        return GameResult(
            delta=bet,
            won=True,
            message=f"Ваши карты: {user_cards} ({user_score})\nДилер: {dealer_cards} ({dealer_score})\nПобеда +{bet}",
        )
    if user_score < dealer_score:
        return GameResult(
            delta=-bet,
            won=False,
            message=f"Ваши карты: {user_cards} ({user_score})\nДилер: {dealer_cards} ({dealer_score})\nПроигрыш -{bet}",
        )
    return GameResult(
        delta=0,
        won=False,
        message=f"Ваши карты: {user_cards} ({user_score})\nДилер: {dealer_cards} ({dealer_score})\nНичья",
    )


def play_guess_number(bet: int, guess: int) -> GameResult:
    secret = random.randint(1, 20)
    if guess == secret:
        win = bet * 2
        return GameResult(delta=win, won=True, message=f"Загадано {secret}. Вы угадали! +{win}")
    hint = "больше" if guess < secret else "меньше"
    return GameResult(delta=-bet, won=False, message=f"Загадано {secret}. Ваше число {hint}. -{bet}")


def play_rps(bet: int, choice: str) -> GameResult:
    bot = random.choice(RPS_OPTIONS)
    wins = {("камень", "ножницы"), ("ножницы", "бумага"), ("бумага", "камень")}
    if choice == bot:
        return GameResult(delta=0, won=False, message=f"Вы: {choice}, бот: {bot}. Ничья")
    if (choice, bot) in wins:
        return GameResult(delta=bet, won=True, message=f"Вы: {choice}, бот: {bot}. Победа +{bet}")
    return GameResult(delta=-bet, won=False, message=f"Вы: {choice}, бот: {bot}. Проигрыш -{bet}")


def play_dice_duel(bet: int) -> GameResult:
    user_roll = random.randint(1, 6) + random.randint(1, 6)
    bot_roll = random.randint(1, 6) + random.randint(1, 6)
    if user_roll > bot_roll:
        return GameResult(delta=bet, won=True, message=f"Ваш бросок: {user_roll}, бот: {bot_roll}. Победа +{bet}")
    if user_roll < bot_roll:
        return GameResult(delta=-bet, won=False, message=f"Ваш бросок: {user_roll}, бот: {bot_roll}. Проигрыш -{bet}")
    return GameResult(delta=0, won=False, message=f"Ваш бросок: {user_roll}, бот: {bot_roll}. Ничья")


def play_slots(bet: int) -> GameResult:
    symbols = ["🍒", "🍋", "🔔", "7", "⭐"]
    reel = [random.choice(symbols) for _ in range(3)]
    if reel[0] == reel[1] == reel[2]:
        win = bet * 5
        return GameResult(delta=win, won=True, message=f"{' '.join(reel)}\nТри в ряд! +{win}")
    if len(set(reel)) == 2:
        win = bet
        return GameResult(delta=win, won=True, message=f"{' '.join(reel)}\nПара! +{win}")
    return GameResult(delta=-bet, won=False, message=f"{' '.join(reel)}\nНе повезло. -{bet}")


class CasinoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🎮 Casino Game Pack")
        self.root.geometry("900x650")

        self.player = PlayerState("Игрок")

        self.name_var = tk.StringVar(value=self.player.name)
        self.bet_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Добро пожаловать! Выберите игру и сделайте ставку.")

        self.roulette_mode = tk.StringVar(value="color")
        self.roulette_color_choice = tk.StringVar(value="красное")
        self.roulette_number_choice = tk.IntVar(value=17)

        self.guess_var = tk.IntVar(value=10)
        self.rps_choice = tk.StringVar(value="камень")

        self._build_ui()
        self.refresh_header()

    def _build_ui(self) -> None:
        wrapper = ttk.Frame(self.root, padding=12)
        wrapper.pack(fill="both", expand=True)

        header = ttk.LabelFrame(wrapper, text="Профиль игрока", padding=10)
        header.pack(fill="x")

        ttk.Label(header, text="Имя:").grid(row=0, column=0, sticky="w")
        ttk.Entry(header, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=8, sticky="w")
        ttk.Button(header, text="Сохранить имя", command=self.update_name).grid(row=0, column=2, padx=8)

        self.stats_label = ttk.Label(header, text="")
        self.stats_label.grid(row=0, column=3, padx=12, sticky="w")

        bet_frame = ttk.LabelFrame(wrapper, text="Ставка", padding=10)
        bet_frame.pack(fill="x", pady=10)
        ttk.Label(bet_frame, text="Сумма:").pack(side="left")
        ttk.Entry(bet_frame, textvariable=self.bet_var, width=10).pack(side="left", padx=8)
        ttk.Label(bet_frame, text="(от 1 до текущего банка)").pack(side="left")

        notebook = ttk.Notebook(wrapper)
        notebook.pack(fill="both", expand=True)

        self._build_high_card_tab(notebook)
        self._build_roulette_tab(notebook)
        self._build_blackjack_tab(notebook)
        self._build_guess_tab(notebook)
        self._build_rps_tab(notebook)
        self._build_dice_tab(notebook)
        self._build_slots_tab(notebook)

        output = ttk.LabelFrame(wrapper, text="Лог игры", padding=8)
        output.pack(fill="both", expand=True, pady=10)

        self.log = tk.Text(output, height=10, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)

        status = ttk.Label(wrapper, textvariable=self.status_var)
        status.pack(fill="x")

    def _build_high_card_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="🃏 Карты")
        ttk.Label(frame, text="Сравнение старшей карты с дилером.").pack(anchor="w")
        ttk.Button(frame, text="Сыграть", command=self.on_high_card).pack(anchor="w", pady=8)

    def _build_roulette_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="🎰 Рулетка")

        ttk.Label(frame, text="Ставка на цвет или точное число.").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Radiobutton(frame, text="Цвет", variable=self.roulette_mode, value="color").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(frame, text="Число", variable=self.roulette_mode, value="number").grid(row=1, column=1, sticky="w")

        ttk.Combobox(
            frame,
            textvariable=self.roulette_color_choice,
            values=["красное", "чёрное"],
            width=12,
            state="readonly",
        ).grid(row=2, column=0, sticky="w", pady=8)

        ttk.Spinbox(frame, from_=0, to=36, textvariable=self.roulette_number_choice, width=6).grid(
            row=2, column=1, sticky="w", pady=8
        )
        ttk.Button(frame, text="Крутить", command=self.on_roulette).grid(row=2, column=2, padx=10, sticky="w")

    def _build_blackjack_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="♠️ 21")
        ttk.Label(frame, text="Автоматический раунд Blackjack (логика дилера и добора).").pack(anchor="w")
        ttk.Button(frame, text="Играть в 21", command=self.on_blackjack).pack(anchor="w", pady=8)

    def _build_guess_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="🔢 Угадай число")

        ttk.Label(frame, text="Угадайте число от 1 до 20 за одну попытку.").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="Ваш вариант:").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.guess_var, width=6).grid(row=1, column=1, sticky="w")
        ttk.Button(frame, text="Проверить", command=self.on_guess).grid(row=1, column=2, padx=10)

    def _build_rps_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="✊ К-Н-Б")

        ttk.Label(frame, text="Камень-ножницы-бумага.").pack(anchor="w")
        choices = ttk.Frame(frame)
        choices.pack(anchor="w", pady=8)
        for option in RPS_OPTIONS:
            ttk.Radiobutton(choices, text=option.capitalize(), variable=self.rps_choice, value=option).pack(side="left", padx=6)
        ttk.Button(frame, text="Сыграть", command=self.on_rps).pack(anchor="w")

    def _build_dice_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="🎲 Кости")

        ttk.Label(frame, text="Бросок двух костей против компьютера.").pack(anchor="w")
        ttk.Button(frame, text="Бросить кости", command=self.on_dice).pack(anchor="w", pady=8)

    def _build_slots_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="🎰 Слоты")

        ttk.Label(frame, text="Слот-машина с комбинациями: три в ряд, пара.").pack(anchor="w")
        ttk.Button(frame, text="Крутить барабаны", command=self.on_slots).pack(anchor="w", pady=8)

    def update_name(self) -> None:
        candidate = self.name_var.get().strip()
        if not candidate:
            messagebox.showwarning("Имя", "Введите имя игрока.")
            return
        self.player.name = candidate
        self.status_var.set(f"Имя обновлено: {candidate}")
        self.refresh_header()

    def refresh_header(self) -> None:
        winrate = (self.player.wins / self.player.games_played * 100) if self.player.games_played else 0.0
        self.stats_label.config(
            text=(
                f"Игрок: {self.player.name} | Фишки: {self.player.chips} | "
                f"Игр: {self.player.games_played} | Побед: {self.player.wins} | Winrate: {winrate:.1f}%"
            )
        )

    def append_log(self, text: str) -> None:
        self.log.config(state="normal")
        self.log.insert("end", text + "\n" + "-" * 50 + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def validated_bet(self) -> int | None:
        try:
            return parse_bet(self.player, self.bet_var.get())
        except ValueError as exc:
            messagebox.showerror("Ставка", str(exc))
            return None

    def apply_result(self, result: GameResult) -> None:
        update_balance(self.player, result)
        self.append_log(result.message)
        self.status_var.set(result.message.splitlines()[-1])
        self.refresh_header()
        if self.player.chips <= 0:
            messagebox.showinfo("Игра окончена", "Фишки закончились. Нажмите OK для перезапуска банка до 200.")
            self.player.chips = 200
            self.refresh_header()

    def on_high_card(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        self.apply_result(play_high_card(self.player, bet))

    def on_roulette(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        mode = self.roulette_mode.get()
        if mode == "color":
            result = play_roulette_color(bet, self.roulette_color_choice.get())
        else:
            result = play_roulette_number(bet, self.roulette_number_choice.get())
        self.apply_result(result)

    def on_blackjack(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        self.apply_result(play_blackjack(bet))

    def on_guess(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        self.apply_result(play_guess_number(bet, self.guess_var.get()))

    def on_rps(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        self.apply_result(play_rps(bet, self.rps_choice.get()))

    def on_dice(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        self.apply_result(play_dice_duel(bet))

    def on_slots(self) -> None:
        bet = self.validated_bet()
        if bet is None:
            return
        self.apply_result(play_slots(bet))


def main() -> None:
    root = tk.Tk()
    CasinoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
