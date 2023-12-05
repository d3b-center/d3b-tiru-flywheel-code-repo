# move all sessions from projects in the 'test' group to a destination project

import flywheel
import os

fw = flywheel.Client(os.getenv('FW_API_KEY'))

destination_proj_id = '64babbf51f1271b09e9921b7' # TIRU_CBTN_full_softcopy

for proj in fw.projects.iter():
    if proj.group == 'test':
        for session in proj.sessions.iter():
            print(f'moving session {session.label} from {proj.label} to TIRU_CBTN_full_softcopy')
            session = fw.get_session(session.id)
            sub_label = session.subject.label
            try:
                session.update({'project': destination_proj_id})
            except:
                # if couldn't update using project ID then see if 
                # it's a duplicate session (already exists in destination)
                # if not a duplicate, then move it using the destination subject ID instead
                dest_sub = fw.lookup(f'tiru/TIRU_CBTN_full_softcopy/{sub_label}')
                ses_list=[]
                for dest_ses in dest_sub.sessions.iter():
                    ses_list.append(dest_ses.label)
                if session.label not in ses_list:
                    session.update({'subject':dest_sub.id})
