# 
import pandas as pd
import os
import flywheel

fw = flywheel.Client(os.getenv('FW_API_KEY'))

# project = fw.lookup('tiru/CBTN_histology_proc')

gear_name = 'prov-gigapath-tile-one-slide'
# gear_name = 'prov-gigapath-extract-tile-embeds'

pending_jobs = fw.jobs.find('state=pending',
                            f'gear_info.name={gear_name}')

jobs_creation_date = f'2025-04-06'
completed_jobs = fw.jobs.find('state=complete',
                              f'gear_info.name={gear_name}',
                              f'created>={jobs_creation_date}')

print(f'N pending jobs:   {len(pending_jobs)}')
print(f'N completed jobs: {len(completed_jobs)}')
