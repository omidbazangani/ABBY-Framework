# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""Test abby.model
"""

import numpy as np
import pandas as pd
import pytest

from abby.model import CatBoostModel, ELMOModel, HammingWeightModel, Model

test_dataset = {
    "instr_stage3": ["LDR", "MULS", "ADDS", "STR", "ADDS"],
    "instr_stage2": ["MULS", "ADDS", "STR", "ADDS", "LDRB"],
    "instr_stage1": ["ADDS", "STR", "ADDS", "LDRB", "MVNS"],
    "power": [0.0616, 0.0577, 0.0929, 0.0774, 0.0807],
    "opcode": [17242, 6523, 25306, 6267, 31131],
}

for i in range(32):
    test_dataset[f"op1_value_previous_{i}"] = [0] * 5
    test_dataset[f"op2_value_previous_{i}"] = [0] * 5
    test_dataset[f"op1_value_current_{i}"] = [0] * 5
    test_dataset[f"op2_value_current_{i}"] = [0] * 5


def test_base_class():
    """Test that model base class cannot predict, fit or save."""
    model = Model("no_path")
    with pytest.raises(NotImplementedError):
        model.predict(None)
    with pytest.raises(NotImplementedError):
        model.fit([[0, 1]], [0.1])
    with pytest.raises(NotImplementedError):
        model.save()


def test_encode_categorical_features():
    """Test categorical features encoding to numerical features."""
    features = pd.DataFrame.from_dict({"instruction": ["STR", "STR", "ADD"]})
    name = "instruction"
    possible_values = ["STR", "LDR", "ADD"]
    r = Model._encode_categorical_features(features, name, possible_values)

    # Check order matches possible_values
    for i, n in enumerate(possible_values):
        assert r.columns[i] == f"{name}_{n}"

    # Check encoding
    assert np.all(r["instruction_STR"] == [1, 1, 0])
    assert np.all(r["instruction_LDR"] == [0, 0, 0])
    assert np.all(r["instruction_ADD"] == [0, 0, 1])


@pytest.mark.parametrize("modelCls", [CatBoostModel])
def test_fitting_model(modelCls):
    """Test model fitting.

    :param modelCls: model class to fit
    :type modelCls: abby.model.Model
    """
    # Load dataset and pop target
    train_features = pd.DataFrame.from_dict(test_dataset)
    train_target = train_features.pop("power")

    # TODO: write CSV to tmp file and fit
    # Create and train new model
    # model = modelCls(None, create=True, task_type="CPU")
    # model.fit(data_files)


@pytest.mark.parametrize("modelCls", [HammingWeightModel])
def test_prediction_model(modelCls):
    """Test model prediction.

    :param modelCls: model class to fit
    :type modelCls: abby.model.Model
    """
    # Load dataset and pop target
    test_features = pd.DataFrame.from_dict(test_dataset)
    test_features.pop("power")

    # Create and train new model
    model = modelCls(create=False)
    model.predict(test_features)
