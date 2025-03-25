import sys


def print_usage():
    print(f"Usage: {sys.argv[0]} <dataset>")
    print("Datasets:")
    print("- emails")
    print("- reviews")


if len(sys.argv) < 2 or "-h" in sys.argv:
    print_usage()
    exit(1)

if sys.argv[1] not in ["emails", "reviews"]:
    print("[-] Error: Dataset does not exist. Please choose a valid dataset")
    print_usage()
    exit(1)

match sys.argv[1]:
    case "emails":
        # TODO: Add email training
        pass
    case "reviews":
        # TODO: Add reviews training
        pass
