
import flywheel

fw = flywheel.Client()

for proj in fw.projects.iter(limit=10):
    if proj.group == 'test':
        try:
            fw.delete_project(proj.id)
            print(f'DELETED: {proj.label}')
        except:
            continue
