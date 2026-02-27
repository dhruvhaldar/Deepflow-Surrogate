import os
import sys
import argparse

def test_path():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str)
    args = parser.parse_args()

    print(f"Received path: {args.output}")
    if args.output:
        expanded = os.path.expanduser(args.output)
        print(f"Expanded path: {expanded}")
        print(f"Is absolute: {os.path.isabs(expanded)}")
        dirname = os.path.dirname(expanded)
        print(f"Dirname: {dirname}")

if __name__ == "__main__":
    test_path()
