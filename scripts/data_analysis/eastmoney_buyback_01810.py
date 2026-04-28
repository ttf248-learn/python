import sys

from eastmoney_buyback import main


if __name__ == "__main__":
    should_pause = len(sys.argv) == 1
    if len(sys.argv) == 1:
        sys.argv.extend(["analyze", "01810"])
    try:
        main()
    finally:
        if should_pause:
            input("\nPress Enter to exit...")
