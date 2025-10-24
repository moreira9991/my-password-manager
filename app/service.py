from random import choice, randint, shuffle

def normalize_site(name: str) -> str:
#Normalize website key to avoid case/whitespace issues.
    return name.strip().lower()


def generate_password() -> str:
#Generate a random password (similar rules to original code)."""
    letters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    numbers = list("0123456789")
    symbols = list("!#$%&()*+")

    password_list = [choice(letters) for _ in range(randint(8, 10))]
    password_list += [choice(numbers) for _ in range(randint(2, 4))]
    password_list += [choice(symbols) for _ in range(randint(2, 4))]
    shuffle(password_list)
    return "".join(password_list)