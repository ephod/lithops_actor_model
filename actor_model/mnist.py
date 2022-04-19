# The code related to the MNIST implementation with NumPY was based on this source code:
#   https://github.com/karynaur/mnist-from-numpy/blob/main/mnist.py
# The author is Aditya Srinivas Menon: https://github.com/karynaur

import logging
import math
import time
from pathlib import Path
from typing import Callable, List, Optional, TypeVar

import matplotlib.pyplot as plt
import numpy as np
from director import Director

T = TypeVar("T")

logger = logging.getLogger(__name__)

np.random.seed(42)

root_folder = Path("./datasets")

assert root_folder.is_dir(), f"Wrong folder: {root_folder}"

TRAINING_SET_IMAGES = root_folder / "train-images-idx3-ubyte"
TRAINING_SET_LABELS = root_folder / "train-labels-idx1-ubyte"

TEST_SET_IMAGES = root_folder / "t10k-images-idx3-ubyte"
TEST_SET_LABELS = root_folder / "t10k-labels-idx1-ubyte"


def fetch(file: Path):
    data = b""
    with file.open("rb") as fh:
        data = fh.read()
    return np.frombuffer(data, dtype=np.uint8).copy()


SKIP_HEXADECIMAL_16 = 0x10
SKIP_DECIMAL_8 = 8
# 3D array: (x, y, z)
# Shape is the number of cells
# Shape: (47_040_016,); Size: 47_040_016
# Shape: (47_040_000,); Size: 47_040_000
# Shape: (60_000, 28, 28); Size: 47_040_000
# Resolution 28 px width x 28 px height
X = fetch(TRAINING_SET_IMAGES)[SKIP_HEXADECIMAL_16:].reshape((-1, 28, 28))
# Shape: (60_008,); Size: 60_008
# Shape: (60_000,); Size: 60_000
Y = fetch(TRAINING_SET_LABELS)[SKIP_DECIMAL_8:]
# Shape: (10_000, 784); Size: 7840000
X_test = fetch(TEST_SET_IMAGES)[SKIP_HEXADECIMAL_16:].reshape((-1, 28 * 28))
# Shape: (10_000,); Size: 10_000
Y_test = fetch(TEST_SET_LABELS)[SKIP_DECIMAL_8:]

# Validation split
rand = np.arange(60_000)
np.random.shuffle(rand)

train_indices = rand[:50_000]
validator_indices = np.setdiff1d(rand, train_indices)

X_train = X[train_indices, :, :]
X_validation = X[validator_indices, :, :]

Y_train = Y[train_indices]
Y_validation = Y[validator_indices]


class Mnist:
    learning_rate = 0
    l1_regularization = None
    l2_regularization = None
    update_l1_regularization = None
    update_l2_regularization = None
    output = None
    director: Optional[Callable[[str, object], None]]

    def set_up(self, learning_rate: float):
        self.learning_rate = learning_rate
        self.l1_regularization = self.initialize_weight(28 * 28, 128)
        self.l2_regularization = self.initialize_weight(128, 10)

    @staticmethod
    def sigmoid(x_val: np.ndarray):
        """Sigmoid.

        Attributes:
            x_val: Shape: (128, 128).
        """
        result = 1 / (np.exp(-x_val) + 1)  # Shape: (128, 128)
        return result

    @staticmethod
    def sigmoid_derivative(x_val):
        """Sigmoid derivative.

        Attributes:
            x_val: Shape: (128, 128).
        """
        numerator = np.exp(-x_val)
        denominator = (np.exp(-x_val) + 1) ** 2
        result = numerator / denominator  # Shape: (128, 128)
        return result

    @staticmethod
    def softmax(x_val):
        """Softmax.

        Attributes:
            x_val: Shape: (128, 10).
        """
        exp_element = np.exp(x_val - x_val.max())
        result = exp_element / np.sum(exp_element, axis=0)  # Shape: (128, 10)
        return result

    @staticmethod
    def softmax_derivative(x_val):
        """Softmax derivative.

        Attributes:
            x_val: Shape: (128, 10).
        """
        exp_element = np.exp(x_val - x_val.max())
        result = (
            exp_element
            / np.sum(exp_element, axis=0)
            * (1 - exp_element / np.sum(exp_element, axis=0))
        )  # Shape: (128, 10)
        return result

    @staticmethod
    def initialize_weight(x_val: int, y_val: int) -> np.ndarray:
        """Initialize weights."""
        layer = np.random.uniform(-1.0, 1.0, size=(x_val, y_val)) / np.sqrt(
            x_val * y_val
        )
        result = layer.astype(np.float32)  # Shape: (784, 128)
        return result

    def forward_backward_pass(self, x_train, y_train, training_actor: str):
        """Forward and backward pass."""
        try:
            targets = np.zeros((len(y_train), 10), np.float32)
            targets[range(targets.shape[0]), y_train] = 1

            x_l1p = x_train.dot(self.l1_regularization)
            x_sigmoid = self.sigmoid(x_l1p)
            x_l2p = x_sigmoid.dot(self.l2_regularization)
            self.output = self.softmax(x_l2p)

            error = (
                2
                * (self.output - targets)
                / self.output.shape[0]
                * self.softmax_derivative(x_l2p)
            )
            self.update_l2_regularization = x_sigmoid.T @ error

            error = (
                self.l2_regularization.dot(error.T)
            ).T * self.sigmoid_derivative(x_l1p)
            self.update_l1_regularization = x_train.T @ error

            self.director(
                training_actor, ("update", (self.output, y_train), {})
            )
            self.stochastic_gradient_descent()
        except TypeError as e:
            print(f"Forward backward pass error: {e}")

    def stochastic_gradient_descent(self):
        self.l1_regularization -= (
            self.learning_rate * self.update_l1_regularization
        )
        self.l2_regularization -= (
            self.learning_rate * self.update_l2_regularization
        )

    def get_output(self):
        return self.output

    def validate(self, x_val, y_val, validation_actor: str) -> None:
        try:
            step_1 = x_val.dot(self.l1_regularization)
            step_2 = self.sigmoid(step_1).dot(self.l2_regularization)
            step_3 = self.softmax(step_2)
            val_out = np.argmax(step_3, axis=1)
            validation_accuracy = (val_out == y_val).mean()
            self.director(
                validation_actor, ("update", (validation_accuracy,), {})
            )
        except TypeError as e:
            print(f"Forward backward pass error: {e}")

    def save_regularizations(self):
        self.director(
            "director",
            ("container", (self.l1_regularization, self.l2_regularization), {}),
        )

    def transfer_to_clone(self, clone: str):
        self.director(
            clone,
            (
                "accept_transfer",
                (
                    self.l1_regularization,
                    self.l2_regularization,
                ),
                {},
            ),
        )

    def accept_transfer(
        self,
        l1_regularization,
        l2_regularization,
    ):
        self.l1_regularization = l1_regularization
        self.l2_regularization = l2_regularization


class Training:
    director: Optional[Callable[[str, object], None]]
    losses: List[float] = None
    accuracies: List[float] = None

    def set_up(self, losses: List[float], accuracies: List[float]):
        self.losses = losses
        self.accuracies = accuracies

    def update(self, output, y_val):
        category: np.ndarray = np.argmax(output, axis=1)
        accuracy = (category == y_val).mean()
        self.accuracies.append(accuracy.item())  # Cast from float64 to float
        loss = ((category - y_val) ** 2).mean()
        self.losses.append(loss.item())  # Cast from float64 to float
        print(f"Training accuracy: {accuracy:.3f}; loss {loss:.3f}")


class Validation:
    director: Optional[Callable[[str, object], None]]
    validation_accuracies: List[float] = None

    def set_up(self, accuracies: List[float]):
        self.validation_accuracies = accuracies

    def update(self, accuracy):
        print(f"Validation accuracy: {accuracy:.3f}")
        self.validation_accuracies.append(accuracy.item())


def main():
    AWS_LAMBDA_TIMEOUT_SECONDS = 150
    start = time.monotonic()
    director = Director()
    director.run()

    current_mnist = 0
    mnist_actor_name = f"mnist_{current_mnist}"
    training_actor_name = f"training_{current_mnist}"
    validation_actor_name = f"validation_{current_mnist}"

    mnist_ps = director.new_actor(Mnist, mnist_actor_name)
    training_ps = director.new_actor(Training, training_actor_name)
    validation_ps = director.new_actor(Validation, validation_actor_name)

    LEARNING_RATE = 0.001
    director.msg_to(mnist_actor_name, ("set_up", (LEARNING_RATE,), {}))
    director.msg_to(training_actor_name, ("set_up", ([], []), {}))
    director.msg_to(validation_actor_name, ("set_up", ([],), {}))

    # Training
    # EPOCHS = 10_000
    EPOCHS = 7_500
    TRAINING_BATCH_SIZE = 128
    wait_seconds = 1

    while director.waiting:
        for i in range(EPOCHS):
            current_time = time.monotonic()
            if math.ceil(current_time - start) > AWS_LAMBDA_TIMEOUT_SECONDS:
                # break
                print("Transferring MNIST")
                start = time.monotonic()

                previous_mnist_actor_name = mnist_actor_name
                previous_validation_actor_name = validation_actor_name
                previous_training_actor_name = training_actor_name

                current_mnist += 1

                mnist_actor_name = f"mnist_{current_mnist}"
                training_actor_name = f"training_{current_mnist}"
                validation_actor_name = f"validation_{current_mnist}"

                director.msg_to(previous_validation_actor_name, "pls stop")
                validation_result = validation_ps.get_result()
                training_ps.clean()

                director.msg_to(previous_training_actor_name, "pls stop")
                training_result = training_ps.get_result()
                validation_ps.clean()

                time.sleep(wait_seconds)

                validation_ps = director.new_actor(
                    Validation, validation_actor_name
                )
                director.msg_to(validation_actor_name, ("set_up", ([],), {}))

                training_ps = director.new_actor(Training, training_actor_name)
                director.msg_to(training_actor_name, ("set_up", ([], []), {}))

                new_mnist_ps = director.new_actor(Mnist, mnist_actor_name)
                director.msg_to(
                    mnist_actor_name, ("set_up", (LEARNING_RATE,), {})
                )
                time.sleep(wait_seconds)
                director.msg_to(
                    previous_mnist_actor_name,
                    ("transfer_to_clone", (mnist_actor_name,), {}),
                )
                time.sleep(wait_seconds)
                director.msg_to(previous_mnist_actor_name, "pls stop")
                mnist_ps.clean()
                mnist_ps = new_mnist_ps

            # Randomize and create batches
            sample = np.random.randint(
                0, X_train.shape[0], size=TRAINING_BATCH_SIZE
            )  # 128 random samples
            x: np.ndarray = X_train[sample].reshape((-1, 28 * 28))
            y: np.ndarray = Y_train[sample]

            # print(f"x {x.size * x.itemsize:d} bytes")
            # print(f"y {y.size * y.itemsize:d} bytes")
            director.msg_to(
                mnist_actor_name,
                ("forward_backward_pass", (x, y, training_actor_name), {}),
            )

            # testing our model using the validation set every 20 epochs
            if i % 20 == 0:
                director.msg_to(
                    mnist_actor_name,
                    (
                        "validate",
                        (
                            X_validation.reshape((-1, 28 * 28)),
                            Y_validation,
                            validation_actor_name,
                        ),
                        {},
                    ),
                )
            if i % 1_000 == 0:
                print(f"For {i}th epoch")
                wait_seconds += 1
                director.msg_to(
                    mnist_actor_name, ("save_regularizations", (), {})
                )
                # print(f'For {i}th epoch: train accuracy: {accuracy:.3f}| validation accuracy:{val_acc:.3f}')
        break

    director.msg_to(mnist_actor_name, ("save_regularizations", (), {}))
    time.sleep(wait_seconds)
    director.msg_to(validation_actor_name, "pls stop")
    director.msg_to(training_actor_name, "pls stop")
    director.msg_to(mnist_actor_name, "pls stop")

    validation_result = validation_ps.get_result()
    training_result = training_ps.get_result()
    mnist_result = mnist_ps.get_result()

    print("Get director container with regularizations")
    l1_reg, l2_reg = director.container

    validation_ps.clean()
    training_ps.clean()
    mnist_ps.clean()
    director.stop()

    np.savez_compressed(
        "weights_compressed", l1=l1_reg, l2=l2_reg
    )  # "weights_compressed.npz"


def read_numpy():
    compressed_file = Path("./weights_compressed.npz")
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
    step_1 = m.dot(data["l1"])
    step_2 = Mnist.sigmoid(step_1).dot(data["l2"])
    x = np.argmax(step_2, axis=1)
    print("First attempt", x)

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
    step_1 = n.dot(data["l1"])
    step_2 = Mnist.sigmoid(step_1).dot(data["l2"])
    x = np.argmax(step_2, axis=1)
    print("Second attempt", x)


if __name__ == "__main__":
    main()
    read_numpy()
