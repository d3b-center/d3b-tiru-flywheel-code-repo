# DICOM decompression
#       Downloads dicoms from Flywheel
#       Decompresses locally using gdcmconv -w
#       Converts resulting files to Nifti
#       Uploads back to the same session on Flywheel in a "Files" acquisition

# ====== user input ====== 
fw_proj_label='PNOC003'
subjs = ['PNOC003-09', 'PNOC003-12', 'PNOC003-16', 'PNOC003-27', 'PNOC003-34', 'PNOC003-36']

import flywheel
import os
from glob import glob
import shutil
import zipfile
import dicom2nifti

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client()

# ====== loop through subjects ====== 
project = fw.projects.find_one(f'label={fw_proj_label}')

completed = []
for sub in project.subjects():
    for ses in sub.sessions():
        count=1
        n_acquisitions=str(len(ses.acquisitions()))
        for acq in ses.acquisitions():
            if ([sub.label,ses.label,acq.label] not in completed) and \
                (sub.label in subjs):
                for file in acq.files:
                    # print(file)
                    if (file.name.endswith('.zip')) and ('dicom' not in file.name):
                        print(f'{sub.label} {ses.label} {file.name}')
                        # download the file
                        acq.download_file(file.name,file.name)
                        # new_fname = file.name.split('.zip')[0]+'.dicom.zip'
                        # os.rename(file.name,new_fname)
                        # acq.upload_file(new_fname)
                        # unzip
                        file_head = file.name.rstrip('.zip')
                        with zipfile.ZipFile(file.name, 'r') as zip_ref:
                            zip_ref.extractall('.')
                        # add ".dcm" file endings
                        count=0
                        for local_file in glob(file_head.rstrip('.dicom')+'/*'):
                            local_file_name = os.path.basename(local_file)
                            new_file_name = os.path.join(os.path.dirname(local_file), f'dicom_{str(count)}.dcm')
                            count+=1
                            if '.dcm' not in local_file_name:
                                os.rename(local_file, new_file_name)
                        # if dicoms were unzipped to current dir, move them to "data/" dir & rename them accordingly
                        if len(glob('*.dcm')) > 0:
                            os.mkdir('data')
                            for dicom in glob('*.dcm'):
                                shutil.move(dicom,'data/')
                        os.rename(next(os.walk('.'))[1][0], file_head)
                        # decompress the DICOMs
                        os.chdir(file_head)
                        for dicom in glob('*'):
                            os.system(f'gdcmconv -w {dicom} {dicom}')
                        os.chdir('..')
                        # convert DICOM to nifti
                        dicom2nifti.convert_directory(file_head, file_head, compression=True, reorient=True)
                        # os.system(f'dcm2niix -f "%d" -p y -z y -b n \"{file_head}\"')
                        target_dir = f'{fw_proj_label}/{sub.label}/{ses.label}/Files/'
                        os.makedirs(target_dir)
                        file_names = glob(f'{file_head}/*.nii.gz')
                        for file2move in file_names:
                            shutil.move(file2move,target_dir)
                        file_names = glob(f'{file_head}/*.bval')
                        for file2move in file_names:
                            shutil.move(file2move,target_dir)
                        file_names = glob(f'{file_head}/*.bvec')
                        for file2move in file_names:
                            shutil.move(file2move,target_dir)
                        # upload fixed files back to Flywheel
                        os.system(f'fw ingest folder --skip-existing --no-audit-log -y -g \'d3b\' -p \'{fw_proj_label}\' \"{fw_proj_label}\"/')
                        print(f'{sub.label}/{ses.label}: acquisistion # {str(count)} out of {n_acquisitions} completed')
                        count+=1
                        completed.append([sub.label,ses.label,acq.label])
                        # delete local files
                        shutil.rmtree(fw_proj_label)
                        shutil.rmtree(file_head)
                        os.remove(file.name)
            else:
                print(f'SKIPPING (already completed): {sub.label} {ses.label} {acq.label}')
