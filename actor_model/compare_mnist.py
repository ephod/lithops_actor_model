import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mnist import Mnist


def read_numpy(file: Path):
    compressed_file = file
    assert compressed_file.is_file(), f"Wrong file: {compressed_file}"
    data = np.load(str(compressed_file), allow_pickle=True)

    # L1 and L2 regularizations
    print(data["l1"])
    print(data["l2"])

    # Number 7
    m = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 10, 10, 10, 0, 0],
        [0, 0, 0, 0, 10, 0, 0],
        [0, 0, 0, 0, 10, 0, 0],
        [0, 0, 0, 0, 10, 0, 0],
        [0, 0, 0, 0, 10, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]

    m = np.concatenate([np.concatenate([[x] * 4 for x in y] * 4) for y in m])
    m = m.reshape(1, -1)
    plt.imshow(m.reshape(28, 28))
    plt.show()
    step_1 = m.dot(data["l1"])
    step_2 = Mnist.sigmoid(step_1).dot(data["l2"])
    x = np.argmax(step_2, axis=1)
    print(f"First attempt: Actual {x}; Expected 7")

    # Number 1
    n = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 10, 0, 0, 0],
        [0, 0, 0, 10, 0, 0, 0],
        [0, 0, 0, 10, 0, 0, 0],
        [0, 0, 0, 10, 0, 0, 0],
        [0, 0, 0, 10, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]

    n = np.concatenate([np.concatenate([[x] * 4 for x in y] * 4) for y in n])
    n = n.reshape(1, -1)
    plt.imshow(n.reshape(28, 28))
    plt.show()
    step_1 = n.dot(data["l1"])
    step_2 = Mnist.sigmoid(step_1).dot(data["l2"])
    x = np.argmax(step_2, axis=1)
    print(f"Second attempt: Actual {x}; Expected 1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--numpy_file",
        type=lambda p: Path(p).absolute(),
        default=Path(__file__).absolute().parent.parent / "weights_compressed.npz",
        help="Path to the Numpy file",
    )

    p = parser.parse_args()
    read_numpy(p.numpy_file)


if __name__ == "__main__":
    main()
