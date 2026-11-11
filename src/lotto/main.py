"""Entry point for the lotto project."""

from lotto import __version__
import csv
import matplotlib.pyplot as plt


def greet(name: str = "world") -> str:
    return f"Hello, {name}! (lotto v{__version__})"

def main() -> None:
    print(greet())
    # read the csv file containing lotto numbers in the data folder 

    with open("data/combined_superlotto.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        recent_10 = rows[-10:]
        n1 = [int(row[3]) for row in recent_10]
        n2 = [int(row[4]) for row in recent_10]
        n3 = [int(row[5]) for row in recent_10]
        n4 = [int(row[6]) for row in recent_10]
        n5 = [int(row[7]) for row in recent_10]

    plt.plot(n1, label="N1")
    plt.plot(n2, label="N2")
    plt.plot(n3, label="N3")
    plt.plot(n4, label="N4")
    plt.plot(n5, label="N5")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
