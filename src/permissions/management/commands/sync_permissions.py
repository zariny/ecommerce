from django.core.management.base import BaseCommand, CommandError

from permissions.collector import sync_enum_permissions


class Command(BaseCommand):
    help = "Synchronize enum permissions with the database."

    def handle(self, *args, **options):
        try:
            sync_enum_permissions()
        except Exception as exc:
            raise CommandError(f"Permission synchronization failed: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS("Enum permissions synchronized successfully.")
        )
