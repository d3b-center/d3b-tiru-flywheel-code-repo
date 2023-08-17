import flywheel
proj_name = 'Sample-Test'
# =================================================================
fw = flywheel.Client('api_key')

project = fw.projects.find_first(f'label={proj_name}')


# Loop over all sessions
for ses in project.sessions.iter():
    ses_label = ses.label
    sub_label = ses.subject.label
    acq= ses.acquisitions
    for acq in ses.acquisitions.iter():
        acq_label=acq.label
        acq_id =acq.id
        for file_obj in acq.files:
            fname = file_obj.name
            file_id =file_obj.file_id
            if fname=='T1CE.nii.gz':#specify which filename need to be renamed
             s = flywheel.models.FileMoveInput(name='file.nii.gz')#specify name of the file to be renamed
             fw.move_file(file_id, s)
