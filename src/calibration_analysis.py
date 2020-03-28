import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from argparse import ArgumentParser

try:
    plt.style.use('scienza')
except OSError:
    print('Could not find scienza matplotlib style, using default')

def normalize_data(df):
    result = df.copy()
    for column_name in result.columns[2:]:
        result[column_name] /= result.iloc[:, 1]
        result[column_name] *= 100
    result.iloc[:, 1] = 100
    return result

def save_calibration_factors(file_name, possible_positions, results_json):
    calibration_data = []
    for case in results_json:
        patient_data = {
                "Case Name" : "",
                "Calibration Factors" : {}
        }
        patient_data["Case Name"] = case["Case Name"]
        patient_factors = {el : 0 for el in possible_positions}
        for position in case["Events"]:
            if position["Type"] in possible_positions:
                p_factor = position["Calibration Factor"]
                p_type = position["Type"]
                patient_factors[p_type] = p_factor
        patient_data["Calibration Factors"] = patient_factors
        calibration_data.append(patient_data)

    with open(file_name, "w") as o_handle:
        json.dump(calibration_data, o_handle, indent=4)

def plot_calibration_factors(file_name, possible_positions):
    with open(file_name, "r") as i_handle:
        calibration_data = json.load(i_handle)
    
    df = pd.DataFrame(
        {"Cases": case["Case Name"], **case["Calibration Factors"]}
        for case in calibration_data
    )
    normalized_df = normalize_data(df)
    print(normalized_df)

    fig = plt.figure(figsize=(10,6))

    n_rows = len(df.index)
    cmap = plt.cm.nipy_spectral
    cmap_list = [cmap(i) for i in range(cmap.N)]
    pd.plotting.parallel_coordinates(
            normalized_df, 
            "Cases",
            color=cmap_list[::int(cmap.N/n_rows)],
            linewidth=0.75
            )
    plt.title("Calibration Factors (SVP)")
    plt.ylabel("Percentage (%)")
    plt.ylim(-50, 150)
    plt.legend(loc="lower left", ncol=4)
    plt.fill_between(possible_positions, 90, 110, color="#b5e2ff")
    plt.show()

def main(args):
    possible_positions = [
        "Supine Spontaneous - 001",
        "Supine CPAP4 - 001",
        "Supine CPAP6 - 001",
        "Supine CPAP8 - 001",
        "Supine Spontaneous - 002"
    ]
    with open(args.calibration_results, "r") as i_handle:
        results_json = json.load(i_handle)

    calibration_data_file = os.path.join(
            os.path.dirname(args.calibration_results),
            "CalibrationFactorsData.json"
    )
    """
    save_calibration_factors(
            calibration_data_file, 
            possible_positions, 
            results_json
    )
    """
    plot_calibration_factors(
            calibration_data_file,
            possible_positions
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "calibration_results"
    )
    main(parser.parse_args())