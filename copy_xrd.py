import os
import pandas as pd
import shutil
from pathlib import Path

base_path = '/Users/vshekar/Google Drive File Stream/My Drive/DARPA SD2 Perovskites/Science/4-Data-Iodides'

all_data = pd.read_csv(
    './data/0042.perovskitedata_RAPID.csv', low_memory=False)

run_name = 'RunID_vial'
missing_plates = set()

for i, row in all_data.iterrows():
    #image_name = row[run_name] + '_side.jpg'
    #file_path = os.path.join('.', 'data', 'images', image_name)
    plate = '_'.join(row[run_name].split('_')[:-1])

    # if not os.path.exists(file_path):
    missing_plates.add(plate)

for plate in missing_plates:
    xrd_path = Path(base_path, plate, 'XRD')
    dest_folder = Path.cwd() / 'data/xrd/xy'
    if xrd_path.exists():
        xrd_filenames = xrd_path.glob('*.xy')
        jpg_filenames = xrd_path.glob('*.jpg')
        # print('----------------')
        # print(list(xrd_filenames))
        for xy_path in xrd_filenames:
            filename = xy_path.name
            dest_path = dest_folder / filename
            shutil.copyfile(xy_path, dest_path)
