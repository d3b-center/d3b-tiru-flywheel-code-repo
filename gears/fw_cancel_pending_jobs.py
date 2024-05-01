import os
import flywheel
import os

# ====== user input ====== 
fw_proj_label='CBTN_ki-67'
fw_group='tiru'
api_key=os.getenv('FW_API_KEY')

gear_name_2_cancel = 'deepliif-predict'

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client(api_key)

# ====== loop through subjects ====== 
grp_cntnr = fw.lookup(fw_group)
proj_cntnr = grp_cntnr.projects.find_first(f'label={fw_proj_label}')

# cancel pendig jobs
for ses_cntr in proj_cntnr.sessions.iter():
    ses_cntr = ses_cntr.reload()
    analyses = ses_cntr.analyses
    matches = [asys for asys in analyses if asys.gear_info.get('name') == gear_name_2_cancel]
    matches = [asys for asys in analyses if asys.job.state in ['pending']]
    for match in matches:
        job = fw.get_job(match.job.id)
        job.change_state('cancelled')
