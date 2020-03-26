import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from argparse import ArgumentParser


def save_calibration_factors(file_name, patient_positions, results_json):
    calibration_data = []
    default_patient_factors = {el : 0 for el in patient_positions}
    default_patient_data = {
            "Case Name" : "",
            "Calibration Factors" : default_patient_factors
    }
    for case in results_json:
        patient_data = dict(default_patient_data)
        patient_data["Case Name"] = case["Case Name"]
        for position in case["Events"]:
            if position["Type"] in patient_positions:
                p_factor = position["Calibration Factor"]
                p_type = position["Type"]
                patient_data["Calibration Factors"][p_type] = p_factor
        calibration_data.append(patient_data)

    with open(file_name, "w") as o_handle:
        json.dump(calibration_data, o_handle, indent=4)

def main(args):
    patient_positions = [
        "Supine Spontaneous - 001",
        "RLD Spontaneous",
        "Prone Spontaneous",
        "LLD Spontaneous",
        "Supine Spontaneous - 002"
    ]
    with open(args.calibration_results, "r") as i_handle:
        results_json = json.load(i_handle)

    calibration_data_file = os.path.join(
            os.path.dirname(args.calibration_results),
            "CalibrationFactorsData.json"
    )
    save_calibration_factors(
            calibration_data_file, 
            patient_positions, 
            results_json
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "calibration_results"
    )
    main(parser.parse_args())

