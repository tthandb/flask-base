import os
from crontab import CronTab
environment = os.getenv('ENVIRONMENT', 'development'),

if __name__ == '__main__':
    manager = CronTab(user=os.getenv('CRONTAB_USER'))

    folder_path = os.path.dirname(os.path.realpath(__file__))
    cronjobs = {
        'auto_payout': {
            'command': 'cd {} && {} run python background_jobs/example.py >> {}/example_log.txt 2>&1'.format( # noqa
                folder_path, os.getenv('CRONTAB_PIPENV_PATH'), folder_path
            ),
            'time_excute': '0 7 * * *'
        }
    }

    has_new_job = False
    for cronjob_name, cronjob_info in cronjobs.items():
        existed_job = list(manager.find_comment(cronjob_name))
        if existed_job:
            print('Cronjob {} existed. Continue!'.format(cronjob_name))
            continue
        print('Create cronjob {}'.format(cronjob_name))
        has_new_job = True
        job = manager.new(
            command=cronjob_info['command'],
            comment=cronjob_name
        )
        job.setall(cronjob_info['time_excute'])

    if has_new_job:
        manager.write()
