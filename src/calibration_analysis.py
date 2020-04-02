import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from argparse import ArgumentParser
from matplotlib.ticker import PercentFormatter

def normalize_data(df):
    result = df.copy()
    for column_name in result.columns[1:]:
        result[column_name] /= result.iloc[:, 0]
        result[column_name] *= 100
    result.iloc[:, 0] = 100
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
            {**case["Calibration Factors"]}
            for case in calibration_data
    )
    normalized_df = normalize_data(df)
    normalized_df = normalized_df.mask(
            np.isclose(normalized_df.values, 0.0000),
    )
    normalized_df.insert(
            0, 
            "Cases", 
            [case["Case Name"] for case in calibration_data]
    )
    print(normalized_df)

    try:
        plt.style.use('scienza')
    except OSError:
        print('Could not find scienza matplotlib style, using default')

    fig = plt.figure(figsize=(9,6))
    n_rows = len(df.index)
    cmap = plt.cm.nipy_spectral
    cmap_list = [cmap(i) for i in range(cmap.N)]
    pd.plotting.parallel_coordinates(
            normalized_df, 
            "Cases",
            color=cmap_list[::int(cmap.N/n_rows)],
            linewidth=1
    )
    plt.title("Calibration Factors (VNI)")
    plt.ylabel("Percentage (%)")
    plt.ylim(-50, 150)
    plt.legend(loc="lower left", ncol=4, fontsize="small")
    plt.fill_between(possible_positions, 90, 110, color="#b5e2ff")
    plt.show()
    plot_calibration_factors_distribution(normalized_df)


def plot_calibration_factors_distribution(df):
    df_dist = (df.iloc[:, 2].values).reshape(-1)
    df_dist = df_dist[~np.isnan(df_dist)]
    """
    plt.hist(
            df_dist, 
            weights = np.ones(len(df_dist)) / len(df_dist),
            bins = np.arange(0, 200, 10)
    )
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.show()
    """
    p10 = df_dist[(df_dist > 90) & (df_dist < 110)].size / float(df_dist.size)
    p20 = df_dist[(df_dist > 80) & (df_dist < 120)].size / float(df_dist.size)

    print("Calibration Factors in the +/-10% range: {}".format(p10))
    print("Calibration Factors in the +/-20% range: {}".format(p20))

def main(args):
    possible_positions = [
            "Spontaneous - 001",
            "CPAP4 - 001",
            "CPAP6 - 001",
            "CPAP8 - 001",
            "CPAP10 - 001",
            "Spontaneous - 002"
    ]
    with open(args.calibration_results, "r") as i_handle:
        results_json = json.load(i_handle)

    calibration_data_file = os.path.join(
            os.path.dirname(args.calibration_results),
            "CalibrationFactorsData.json"
    )
    
    save_calibration_factors(
            calibration_data_file, 
            possible_positions, 
            results_json
    )
    
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