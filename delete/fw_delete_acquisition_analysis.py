import flywheel

fw = flywheel.Client()

fw.delete_acquisition_analysis('60dccefcd91dce413a133a8d','60dccefcd91dce413a133a8d') # acquisition_id, analysis_id
fw.delete_acquisition('60dc9b9eb6b1fdee3c13444f')

session = fw.get_session('60dc9b9db6b1fdee3c134443')
for acq in session.acquisitions.iter():
    if not acq.files:
        # print(acq.label)
        try:
            fw.delete_acquisition(acq.id)
            print('Deleted acquisition: '+acq.label)
        except Exception as e:
            analysis_id = str(e)[-26:-2] # hardcoded to get id from error output
            analysis = fw.get_analysis(analysis_id)
            parent_id = analysis.parent.id
            fw.delete_acquisition_analysis(parent_id,analysis_id) # acquisition_id, analysis_id
            fw.delete_acquisition(acq.id)
            print('Deleted acquisition: '+acq.label)
