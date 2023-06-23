import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam

class ChessValueDataset(tf.keras.utils.Sequence):
    def __init__(self):
        dat = np.load("data/dataset_5M.npz")
        self.X = dat['arr_0']
        self.Y = dat['arr_1']
        print("loaded", self.X.shape, self.Y.shape)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]

class Net(tf.keras.Model):
    def __init__(self):
        super(Net, self).__init__()
        self.a1 = layers.Conv2D(16, kernel_size=3, padding='same')
        self.a2 = layers.Conv2D(16, kernel_size=3, padding='same')
        self.a3 = layers.Conv2D(32, kernel_size=3, strides=2)

        self.b1 = layers.Conv2D(32, kernel_size=3, padding='same')
        self.b2 = layers.Conv2D(32, kernel_size=3, padding='same')
        self.b3 = layers.Conv2D(64, kernel_size=3, strides=2)

        self.c1 = layers.Conv2D(64, kernel_size=2, padding='same')
        self.c2 = layers.Conv2D(64, kernel_size=2, padding='same')
        self.c3 = layers.Conv2D(128, kernel_size=2, strides=2)

        self.d1 = layers.Conv2D(128, kernel_size=1)
        self.d2 = layers.Conv2D(128, kernel_size=1)
        self.d3 = layers.Conv2D(128, kernel_size=1)

        self.last = layers.Dense(1)

    def call(self, x):
        x = tf.nn.relu(self.a1(x))
        x = tf.nn.relu(self.a2(x))
        x = tf.nn.relu(self.a3(x))

        x = tf.nn.relu(self.b1(x))
        x = tf.nn.relu(self.b2(x))
        x = tf.nn.relu(self.b3(x))

        x = tf.nn.relu(self.c1(x))
        x = tf.nn.relu(self.c2(x))
        x = tf.nn.relu(self.c3(x))

        x = tf.nn.relu(self.d1(x))
        x = tf.nn.relu(self.d2(x))
        x = tf.nn.relu(self.d3(x))

        x = tf.reshape(x, (-1, 128))
        x = self.last(x)

        return tf.tanh(x)

if __name__ == "__main__":
    chess_dataset = ChessValueDataset()
    train_loader = tf.data.Dataset.from_generator(chess_dataset.__getitem__, output_signature=(
        tf.TensorSpec(shape=chess_dataset[0][0].shape, dtype=tf.float32),
        tf.TensorSpec(shape=chess_dataset[0][1].shape, dtype=tf.float32)
    )).batch(256).shuffle(True)

    model = Net()
    optimizer = Adam()

    @tf.function
    def train_step(data, target):
        with tf.GradientTape() as tape:
            output = model(data)
            loss = tf.reduce_mean(tf.losses.mean_squared_error(target, output))
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        return loss

    for epoch in range(100):
        all_loss = 0
        num_loss = 0
