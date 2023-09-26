# deletes all analysis containers for a specified gear
#   at the session-level
#
#   amf 09-2023

import flywheel
import os

fw = flywheel.Client(os.getenv('FW_API_KEY'))

proj_label = 'TIRU_proc_data'
gear_name = 'd3b-copy-proc-2-acq' # gear to delete all associated containers

proj_cntr = fw.projects.find_first(f'label={proj_label}')

for session in proj_cntr.sessions.iter():
    session = session.reload()
    for asys in session.analyses:
        if gear_name in asys.label: # assumes the gear_name will be in the job label
            print(f'DELETING: {asys.label}')
            parent_id = asys.parent.id
            fw.delete_session_analysis(asys.parent.id, asys.id) # acquisition_id, analysis_id
