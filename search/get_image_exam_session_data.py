# Find session (manufacturer, magnetic field strength, model) information
# on Flywheel for a list of subjects/sessions

import os
import pandas as pd
import flywheel

fw = flywheel.Client(os.getenv('FW_API_KEY'))

in_fn = 'nnunet_deface_cohort.csv' # CSV with two columns: "CBTN Subject ID" and "Session" (age in days at imaging)
sub_df = pd.read_csv(in_fn)
sub_df = sub_df.dropna(axis=0)

# for each subject, look up their session on Flywheel 
# in the main CBTN "_v2" projects, then loop through the 
# files in the session to try to find corresponding exam information
for ind,row in sub_df.iterrows():
    print(f'Processing subject {ind}/{len(sub_df)}')
    sub_id = row['CBTN Subject ID']
    ses_age =  str(int(row['Session']))
    query = f'subject.label == {sub_id} AND '\
            f'session.label CONTAINS {ses_age}'
    # print(query)
    matching_sessions = fw.search({'structured_query': query, 'return_type': 'session'}, size=10000)
    manufacturer = []
    mag_field_strength = []
    model = []
    for session in matching_sessions:
        if '_v2' in session.project.label:
            # print(session.project.label)
            session = fw.get(session.session.id)
            for acq in session.acquisitions():
                for file in acq.files:
                    if (manufacturer==[]) | (mag_field_strength==[]) | (model==[]):
                        if 'nii.gz' in file.name:
                            file = file.reload()
                            # print(file.name)
                            if manufacturer == []:
                                try:
                                    manufacturer = file.info['Manufacturer']
                                except:
                                    continue
                            if mag_field_strength == []:
                                try:
                                    mag_field_strength = file.info['MagneticFieldStrength']
                                except:
                                    continue
                            if model == []:
                                try:
                                    model = file.info['ManufacturersModelName']
                                except:
                                    continue
    if (manufacturer==[]) & (mag_field_strength==[]) & (model==[]):
        manufacturer='NaN'
        mag_field_strength='NaN'
        model='NaN'
    sub_ind = sub_df[sub_df['CBTN Subject ID']==sub_id].index.to_list()[0]
    sub_df.loc[sub_ind,'Manufacturer'] = manufacturer
    sub_df.loc[sub_ind,'MagneticFieldStrength'] = mag_field_strength
    sub_df.loc[sub_ind,'ManufacturersModelName'] = model

sub_df.to_csv('imaging_data.csv',index=False)
