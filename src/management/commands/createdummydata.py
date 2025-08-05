from django.core.management import BaseCommand
from sandbox.dummy import run


class Command(BaseCommand):
    def handle(self, *args, **options):
        flag = run(flag=True)
        if flag:
            print("Done.")
        else:
            print("Something went wrong!")
