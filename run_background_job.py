import os
import time
import click
from dotenv import load_dotenv
from background_jobs.example import Example

@click.command()
@click.option('-w', '--background_job', type=str, required=True,
              help='Worker name')
def run_background_job(background_job):
    load_dotenv()
    # example
    if background_job == 'example':
        background = Example()
        time_repeat = 60
    else:
        click.echo('Background [{}] not found!'.format(background_job))
        return

    while True:
        try:
            background.run()
        except Exception as error:
            print(error)
        time.sleep(time_repeat)


if __name__ == '__main__':
    run_background_job()
