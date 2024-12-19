from django_cron import CronJobBase, Schedule

class MyCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=1)
    code = 'users.my_cron_job'

    def do(self):
        print("Running scheduled task...")
