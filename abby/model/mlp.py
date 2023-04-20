# Copyright (C) 2020-2021
# SPDX-License-Identifier: Apache-2.0

"""
MLP model

You should NOT use Numpy or Pandas here, it does not scale up!
Please use Tensorflow equivalents.
"""

import logging

from abby.model.base import Model

# Local logger
log = logging.getLogger(__name__)


class MlpModel(Model):
    """Multi-Layer Perceptron model

    Placeholder for future implementation.
    """

    def __init__(self, path, create=False):
        """Initialize tensorflow model

        :param path: path to load or save model
        :type path: str
        :param create: create new model without loading, defaults to False
        :type create: bool, optional
        """
        self.path = path
        self.model = None

        # Load existing model
        if not create:
            import tensorflow as tf

            self.model = tf.keras.models.load_model(path)

    @staticmethod
    def _build_preprocessing_model(inputs):
        """Build preprocessing keras model."""
        import tensorflow as tf

        # Do not process numeric inputs
        preprocessed_inputs = [v for v in inputs.values() if v.dtype == tf.float16]

        # Encode categorical features
        for v in inputs.values():
            if v.dtype == tf.float16:
                continue
            x = tf.keras.layers.experimental.preprocessing.StringLookup()(v)
            x = tf.keras.layers.experimental.preprocessing.CategoryEncoding(
                max_tokens=80
            )(x)
            preprocessed_inputs.append(x)

        # Concatenate everything
        inputs_concat = tf.keras.layers.Concatenate()(preprocessed_inputs)
        preprocessing_model = tf.keras.Model(inputs, inputs_concat)
        return preprocessing_model

    @staticmethod
    def _preprocess_data(features, label=None):
        """Preprocess data."""
        import tensorflow as tf

        # Collect name of all 32bits features
        bin_features = [n for n, y in features.items() if y.dtype != object]

        # Create "binary" filter
        for name in bin_features:
            features[name] = tf.cast(features[name], dtype=tf.int64)
            features[name] = tf.expand_dims(features[name], 1)
            features[name] = tf.bitwise.right_shift(
                features[name], tf.range(32, dtype=tf.int64)
            )
            features[name] = tf.math.mod(features[name], 2)
            features[name] = tf.cast(features[name], dtype=tf.float16)

        return features, label

    def predict(self, features):
        """Predict target using features

        :param features: features to input to the model
        :type features: pandas.DataFrame
        :return: model prediction
        :rtype: numpy.ndarray
        """
        import tensorflow as tf

        features = tf.data.Dataset.from_tensor_slices(
            {f: [features[f].values] for f in features.keys()}
        ).map(self._preprocess_data)
        return self.model.predict(features)

    def fit(self, data_files, test_size=0.2, batch_size=100000):
        """Fit model on target using provided data

        For profiler support, if you get ``CUPTI_ERROR_INSUFFICIENT_PRIVILEGES``
        then you might need to add an option to the nvidia kernel module.
        Edit ``/etc/modprobe.d/nvidia-kernel-common.conf`` and add
        ``options nvidia "NVreg_RestrictProfilingToAdminUsers=0"``.
        Then rebuild your initramfs (``update-initramfs -u``) and reboot.

        :param data_files: dataset files
        :type data_files: [str]
        :param test_size: portion of the dataset using for evaluation, default
            to 0.2
        :type test_size: float, optional
        :param batch_size: number of records to combine in a single batch,
            default to 100000
        :type batch_size: int, optional
        """
        import tensorflow as tf

        # Load CSV files in batch, shuffle and prefetch
        train_files = data_files[: int(test_size * len(data_files))]
        validation_files = data_files[int(test_size * len(data_files)) :]
        train_set = (
            tf.data.experimental.make_csv_dataset(
                train_files,
                batch_size,
                label_name="power",
                num_epochs=1,
                num_parallel_reads=10,
            )
            .map(self._preprocess_data, num_parallel_calls=tf.data.AUTOTUNE)
            .cache()
        )
        validation_set = (
            tf.data.experimental.make_csv_dataset(
                validation_files,
                batch_size,
                label_name="power",
                num_epochs=1,
                num_parallel_reads=10,
            )
            .map(self._preprocess_data, num_parallel_calls=tf.data.AUTOTUNE)
            .cache()
        )

        # Symbolic keras.Input objects, matching the names and data-types of the
        # CSV columns
        inputs = {}
        features_set = train_set.map(lambda x, y: x)
        for features in features_set.take(1):
            for name, column in features.items():
                dtype = column.dtype
                if dtype == object:
                    inputs[name] = tf.keras.Input(
                        shape=(1,), name=name, dtype=tf.string
                    )
                else:
                    inputs[name] = tf.keras.Input(
                        shape=(32,), name=name, dtype=tf.float16
                    )

        # Build keras model
        body = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(16, activation="relu"),
                tf.keras.layers.Dense(16, activation="relu"),
                tf.keras.layers.Dense(1),
            ]
        )
        preprocessing_model = self._build_preprocessing_model(inputs)
        preprocessed_inputs = preprocessing_model(inputs)
        outputs = body(preprocessed_inputs)
        self.model = tf.keras.Model(inputs, outputs)
        self.model.compile(
            loss=tf.losses.MeanSquaredError(),
            optimizer=tf.optimizers.Adam(learning_rate=0.003),
            metrics=[tf.keras.metrics.RootMeanSquaredError()],
        )

        # Create callbacks
        filename = self.path.split("/")[-1]
        logdir = f"logs/{filename}"
        tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=logdir,
            profile_batch=(3, 6),
        )
        estop_callback = tf.keras.callbacks.EarlyStopping(patience=30)
        checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=logdir + "/model_{epoch:02d}",
            save_best_only=True,  # only save a model if `val_loss` has improved
            monitor="val_loss",
            verbose=1,
        )

        # Validation is done after each epoch
        self.model.fit(
            train_set,
            epochs=1000,
            validation_data=validation_set,
            callbacks=[tensorboard_callback, estop_callback, checkpoint_callback],
        )

    def save(self):
        """Save model to path provided

        You can append `.h5` to use the HDF5 standard.
        """
        if self.model is None:
            log.error("Cannot save empty model.")
            exit(1)

        log.debug(f"Saving power model at {self.path}")
        self._create_parent_folder(self.path)
        self.model.save(self.path)
