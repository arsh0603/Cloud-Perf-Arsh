from django.core.management.base import BaseCommand
from myapp.models import PersistentCache

class Command(BaseCommand):
    help = 'Clean up expired persistent cache entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        stats_before = PersistentCache.get_stats()
        
        self.stdout.write(
            self.style.SUCCESS(f'Persistent Cache Stats Before Cleanup:')
        )
        self.stdout.write(f'Total entries: {stats_before["total_entries"]}')
        self.stdout.write(f'Details entries: {stats_before["details_count"]}')
        self.stdout.write(f'Graph entries: {stats_before["graph_count"]}')
        self.stdout.write(f'Expired entries: {stats_before["expired_count"]}')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {stats_before["expired_count"]} expired entries')
            )
            return
        
        # Perform cleanup
        deleted_count = PersistentCache.cleanup_expired()
        
        stats_after = PersistentCache.get_stats()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {deleted_count} expired entries')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Remaining entries: {stats_after["total_entries"]}')
        )
