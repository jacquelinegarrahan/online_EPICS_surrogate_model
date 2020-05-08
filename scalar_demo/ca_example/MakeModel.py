import numpy as np
import matplotlib.pyplot as plt
import sys, os
import keras
import tensorflow
from keras.models import Sequential, Model, model_from_json
from keras.layers import Input, Dense, Activation
import h5py
import random
import time


class SurrogateModel:
    """ 
Example Usage:
    Load model and use a dictionary of inputs to evaluate the NN.
    """

    def __init__(self, model_file=None):
        # Save init
        self.model_file = model_file

        # Run control
        self.configure()

    def __str__(self):
        s = f"""The inputs are: {', '.join(self.input_names)} and the outputs: {', '.join(self.output_names)}"""
        return s

    def configure(self):

        ## Open the File
        with h5py.File(self.model_file, "r") as h5:
            attrs = dict(h5.attrs)
        self.__dict__.update(attrs)
        self.json_string = self.JSON
        self.model = model_from_json(self.json_string.decode("utf-8"))
        self.model.load_weights(self.model_file)
        ## Set basic values needed for input and output scaling
        self.model_value_max = attrs["upper"]
        self.model_value_min = attrs["lower"]

    def scale_inputs(self, input_values):
        data_scaled = self.model_value_min + (
            (input_values - self.input_offsets)
            * (self.model_value_max - self.model_value_min)
            / self.input_scales
        )
        return data_scaled

    def scale_outputs(self, output_values):
        data_scaled = self.model_value_min + (
            (output_values - self.output_offsets)
            * (self.model_value_max - self.model_value_min)
            / self.output_scales
        )
        return data_scaled

    def predict(self, input_values):
        inputs_scaled = self.scale_inputs(input_values)
        predicted_outputs = self.model.predict(inputs_scaled)
        predicted_outputs_unscaled = self.unscale_outputs(predicted_outputs)
        return predicted_outputs_unscaled

    def unscale_inputs(self, input_values):
        data_unscaled = (
            (input_values - self.model_value_min)
            * (self.input_scales)
            / (model_value_max - model_value_min)
        ) + self.input_offsets
        return data_unscaled

    def unscale_outputs(self, output_values):
        data_unscaled = (
            (output_values - self.model_value_min)
            * (self.output_scales)
            / (self.model_value_max - self.model_value_min)
        ) + self.output_offsets
        return data_unscaled

    def run(self, settings, request=None, verbose=False):
        t = time.time()
        results = self.evaluate(settings)
        if verbose:
            print("Running model. Time ellapsed: " + str(time.time() - t) + " (secs).")

        return results

    def evaluate(self, settings):
        vec = np.array([[settings[key] for key in self.input_ordering]])
        model_output = self.predict(vec)
        output = dict(zip(self.output_ordering, model_output.T))
        return output
