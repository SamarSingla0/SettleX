from django.core.management.base import BaseCommand
from finance.services.dataset_generator import SyntheticDatasetGenerator


class Command(BaseCommand):
    help = "Generates a realistic synthetic financial dataset (50, 100, 150, 500 records) with Ground Truth."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=150,
            choices=[50, 100, 150, 500],
            help="Number of synthetic records to generate (default: 150)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for repeatable data generation (default: 42)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        self.stdout.write(self.style.NOTICE(f">>> Initializing Synthetic Dataset Generator for {count} records (Seed: {seed})..."))
        
        generator = SyntheticDatasetGenerator(record_count=count, seed=seed, export_csv=True)
        stats = generator.generate()

        self.stdout.write(self.style.SUCCESS(f"[+] Successfully generated {stats['total_records']} records:"))
        for scenario, cnt in stats["distribution"].items():
            self.stdout.write(f"    - {scenario:<25}: {cnt} records")

        self.stdout.write(f"[*] Payments Created      : {stats['payments_count']}")
        self.stdout.write(f"[*] Gateway Transactions  : {stats['gateway_count']}")
        self.stdout.write(f"[*] Bank Transactions     : {stats['bank_count']}")
        self.stdout.write(f"[*] Ground Truth Records  : {stats['ground_truth_count']}")
        self.stdout.write(self.style.SUCCESS("[+] CSV files exported to 'data/' folder successfully."))