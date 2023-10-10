import shutil
import os
import flywheel

os.system('export FLYWHEEL_SDK_REQUEST_TIMEOUT=600')

def move_file(fw, source_acq_cntr, old_fname, dest_acq_cntr, new_fname):
    fw.download_file_from_acquisition(source_acq_cntr.id, old_fname, old_fname)
    shutil.move(old_fname, new_fname)
    dest_acq_cntr.upload_file(new_fname)
    fw.delete_acquisition_file(source_acq_cntr.id, old_fname)
    os.remove(new_fname)

def get_or_make_fw_subject(proj_cntr, sub_label):
    # check if subject already exists, if not then create it
    proj_cntr = proj_cntr.reload()
    dest_sub_cntr = proj_cntr.subjects.find(f'label={sub_label}')
    if dest_sub_cntr == []:
        dest_sub_cntr = proj_cntr.add_subject(label=sub_label)
    else:
        dest_sub_cntr = dest_sub_cntr[0]
    return dest_sub_cntr

def get_or_make_fw_session(sub_cntr, ses_label):
    dest_ses_cntr = sub_cntr.sessions.find(f'label={ses_label}')
    if dest_ses_cntr == []:
        dest_ses_cntr = sub_cntr.add_session(label=ses_label)
    else:
        dest_ses_cntr = dest_ses_cntr[0]
    return dest_ses_cntr

def get_or_make_fw_acquisition(session_cntr, acq_label):
    if session_cntr.acquisitions.find(f'label={acq_label}') == []:
        dest_acq_cntr = session_cntr.add_acquisition(label=acq_label)
    else:
        dest_acq_cntr = session_cntr.acquisitions.find(f'label={acq_label}')[0]
    return dest_acq_cntr

def get_destination_acquisition(fw, dest_proj_cntr, source_acq_cntr):
# assumes the destination project exists
    source_sub = fw.get(source_acq_cntr.parents['subject'])
    source_ses = fw.get(source_acq_cntr.parents['session'])
    # if subject doesn't exist in destination, create it
    dest_subj = get_or_make_fw_subject(dest_proj_cntr, source_sub.label)
    # if session doesn't exist in destination, create it
    dest_ses = get_or_make_fw_session(dest_subj, source_ses.label)
    # if acquisition doesn't exist in destination, create it
    dest_acq = get_or_make_fw_acquisition(dest_ses, source_acq_cntr.label)
    return dest_acq

def move_acquisition(fw, dest_proj_cntr, acq_cntr):
    dest_acq = get_destination_acquisition(fw, dest_proj_cntr, acq_cntr)
    # now move the file(s)
    for file in acq_cntr.files:
        move_file(fw, acq_cntr, file.name, dest_acq, file.name)
    acq_cntr = acq_cntr.reload()
    if not acq_cntr.files:
        fw.delete_acquisition(acq_cntr.id)

def delete_empty_fw_acquisition(fw, acq):
    try:
        acq = acq.reload()
    except:
        acq = acq
    if not acq.files:
        fw.delete_acquisition(acq.id)

def move_session(fw, session, destination_proj_cntr):
    session = session.reload()
    session = fw.get_session(session.id)
    try:
        session.update({'project': destination_proj_cntr.id})
    except:
        sub_label = session.subject.label
        dest_sub_cntr = get_or_make_fw_subject(destination_proj_cntr, sub_label)
        session.update({'subject': dest_sub_cntr.id})

def change_fw_session_label(fw, session_cntr, new_session_label):
    ses_body = flywheel.models.Session(label = new_session_label)
    fw.modify_session(session_cntr.id, ses_body)

def change_fw_subject_label(fw, subject_cntr, new_sub_label):
    sub_body = flywheel.models.Subject(label = new_sub_label)
    fw.modify_subject(subject_cntr.id, sub_body)

def change_fw_acq_label(fw, acq_cntr, new_acq_label):
    body = flywheel.models.Acquisition(label = new_acq_label)
    fw.modify_acquisition(acq_cntr.id, body)
