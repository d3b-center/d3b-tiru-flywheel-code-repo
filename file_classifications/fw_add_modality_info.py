import flywheel
fw = flywheel.Client()

template = fw.get_modality('MR')
template['classification']['Contrast'] = ['Contrast', 'No Contrast']
template_id = template.pop('_id')
fw.replace_modality(template_id, template)
