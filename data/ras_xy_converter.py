import os
from glob import glob

import pandas as pd
import numpy as np


def rescale_xrd_df_from_different_sources(input_haverford_df, lbl_wavelength=1.79, haverford_wavelength=1.54):
    """
    This function applies Bragg's law to re-scale the XRD data from different measurement sources via d spacing.

    lambda_1/(2*sin(theta_1) = d = lambda_2/(2*sin(theta_2)


    Per Zhi Li, LBNL uses a Co source (1.79A wavelength) and HC uses a Cu source (1.54A wavelength).
    :param input_haverford_df: a pandas dataframe representing a Haverford XY file with two columns: two_theta and intensity
    :return: As dict keyed by run_id, valued with the row from the leaderboard
   """
    returned_df = input_haverford_df.copy()
    lambda_ratio = lbl_wavelength / haverford_wavelength
    haverford_theta_radians = (np.pi / 180) * input_haverford_df['two_theta'] / 2
    sin_theta_haverford = np.sin(haverford_theta_radians)
    sin_theta_lbl = lambda_ratio * sin_theta_haverford
    theta_lbl_radians = np.arcsin(sin_theta_lbl)
    theta_lbl_degrees = theta_lbl_radians * 180 / np.pi
    returned_df['two_theta'] = 2 * theta_lbl_degrees
    return returned_df


def parse_ras(ras_file_path):
    with open(ras_file_path, 'r', encoding="SHIFT_JIS") as infile:
        parse = False
        xy_data = {'x': [], 'y': []}
        for line in infile.readlines():
            if line.strip() == '*RAS_INT_START':
                parse = True
                continue
            elif line.strip() == '*RAS_INT_END':
                parse = False
                continue
            elif parse:
                values = line.split()
                xy_data['x'].append(float(values[0]))
                xy_data['y'].append(float(values[1]))
        data = pd.DataFrame.from_dict(xy_data)
        return data


if __name__ == '__main__':
    """
    runs on files downloaded from:
    pXRD for Lead Iodide: https://drive.google.com/open?id=1vAjlj-w-n74LgKPuGJzRlr0E8Zhx4yN2
    Pristine amine pXRD: https://drive.google.com/open?id=1zFOQo8w0UR7PIgSL3qY_q698OHhdYoZE
    """

    ras_filenames = glob("ras/*/*.ras")

    for filename in ras_filenames:
        df = parse_ras(filename)
        xy_filename = os.path.basename(filename).replace('.ras', '.xy').replace(' ', '_')
        file_basename = os.path.basename(filename).replace('.ras', '').replace(' ', '_')
        df.columns = ['two_theta', 'intensity']
        rescaled_df = rescale_xrd_df_from_different_sources(df)

        rescaled_filename = xy_filename.replace('.xy', '.lbl_rescaled.xy')
        with open(os.path.join('ras_xy', rescaled_filename), 'w') as fout:
            fout.write("# Processed xy data with Haverford two-theta converted to LBL scale\n")
            df.to_csv(fout, index=False)