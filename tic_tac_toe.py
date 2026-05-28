"""Tic Tac Toe game in Python — play against a friend or the computer."""

import random
import sys


def create_board():
    return [" "] * 9


def display_board(board):
    print()
    for row in range(3):
        cells = [board[row * 3 + col] for col in range(3)]
        print(f" {cells[0]} | {cells[1]} | {cells[2]} ")
        if row < 2:
            print("---+---+---")
    print()


def get_available_moves(board):
    return [i for i, cell in enumerate(board) if cell == " "]


def check_winner(board, player):
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
        (0, 4, 8), (2, 4, 6),              # diagonals
    ]
    return any(board[a] == board[b] == board[c] == player for a, b, c in wins)


def is_draw(board):
    return " " not in board


def minimax(board, is_maximizing):
    if check_winner(board, "O"):
        return 1
    if check_winner(board, "X"):
        return -1
    if is_draw(board):
        return 0

    if is_maximizing:
        best = -float("inf")
        for move in get_available_moves(board):
            board[move] = "O"
            best = max(best, minimax(board, False))
            board[move] = " "
        return best
    else:
        best = float("inf")
        for move in get_available_moves(board):
            board[move] = "X"
            best = min(best, minimax(board, True))
            board[move] = " "
        return best


def computer_move(board, difficulty):
    available = get_available_moves(board)
    if not available:
        return

    if difficulty == "easy":
        move = random.choice(available)
    elif difficulty == "medium":
        # 50% chance of optimal move, 50% random
        if random.random() < 0.5:
            move = random.choice(available)
        else:
            move = best_move(board)
    else:  # hard
        move = best_move(board)

    board[move] = "O"
    return move


def best_move(board):
    best_score = -float("inf")
    best_pos = None
    for move in get_available_moves(board):
        board[move] = "O"
        score = minimax(board, False)
        board[move] = " "
        if score > best_score:
            best_score = score
            best_pos = move
    return best_pos


def human_move(board, player):
    while True:
        try:
            pos = input(f"Player {player}, enter position (1-9): ")
            pos = int(pos) - 1
            if pos < 0 or pos > 8:
                print("Please enter a number between 1 and 9.")
                continue
            if board[pos] != " ":
                print("That position is already taken. Try again.")
                continue
            board[pos] = player
            return pos
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")


def show_position_guide():
    print("\nPosition guide:")
    print(" 1 | 2 | 3 ")
    print("---+---+---")
    print(" 4 | 5 | 6 ")
    print("---+---+---")
    print(" 7 | 8 | 9 ")
    print()


def choose_difficulty():
    while True:
        print("\nSelect difficulty:")
        print("  1. Easy")
        print("  2. Medium")
        print("  3. Hard (unbeatable)")
        choice = input("Enter choice (1-3): ").strip()
        if choice in ("1", "easy"):
            return "easy"
        if choice in ("2", "medium"):
            return "medium"
        if choice in ("3", "hard"):
            return "hard"
        print("Invalid choice. Please try again.")


def play_game():
    print("=" * 35)
    print("   Welcome to Tic Tac Toe!")
    print("=" * 35)

    while True:
        print("\nGame modes:")
        print("  1. Player vs Player")
        print("  2. Player vs Computer")
        mode = input("Choose mode (1 or 2): ").strip()

        if mode not in ("1", "2"):
            print("Invalid choice. Please enter 1 or 2.")
            continue

        difficulty = None
        if mode == "2":
            difficulty = choose_difficulty()

        board = create_board()
        show_position_guide()
        current_player = "X"

        while True:
            display_board(board)

            if mode == "2" and current_player == "O":
                print("Computer is thinking...")
                move = computer_move(board, difficulty)
                print(f"Computer placed O at position {move + 1}.")
            else:
                human_move(board, current_player)

            if check_winner(board, current_player):
                display_board(board)
                if mode == "2" and current_player == "O":
                    print("Computer wins! Better luck next time.")
                else:
                    print(f"Player {current_player} wins! Congratulations!")
                break

            if is_draw(board):
                display_board(board)
                print("It's a draw!")
                break

            current_player = "O" if current_player == "X" else "X"

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing! Goodbye.")
            break


if __name__ == "__main__":
    try:
        play_game()
    except (KeyboardInterrupt, EOFError):
        print("\nGame interrupted. Goodbye!")
        sys.exit(0)
