import csv
from django.core.management.base import BaseCommand
from claims.models import Claim


class Command(BaseCommand):
    help = "Import LIAR dataset TSV into Claim table"

    def add_arguments(self, parser):
        parser.add_argument("--split", required=True, choices=["train", "test", "valid"])
        parser.add_argument("--path", required=True)

    def handle(self, *args, **opts):
        split = opts["split"]
        path = opts["path"]

        created = 0
        skipped_empty = 0
        skipped_short = 0

        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")

            for line_num, row in enumerate(reader, start=1):
                # Skip completely empty lines
                if not row or all((c.strip() == "" for c in row)):
                    skipped_empty += 1
                    continue

                # LIAR should have 14 columns (0..13). If fewer, skip (or pad).
                if len(row) < 14:
                    skipped_short += 1
                    # If you prefer padding instead of skipping, comment the next line
                    continue

                # Trim to exactly 14 in case there are extras
                row = row[:14]

                Claim.objects.create(
                    liar_id=row[0],
                    label=row[1],
                    statement=row[2],
                    subjects=row[3],
                    speaker=row[4],
                    speaker_job_title=row[5],
                    state=row[6],
                    party=row[7],
                    barely_true_count=int(row[8]) if row[8].strip() else 0,
                    false_count=int(row[9]) if row[9].strip() else 0,
                    half_true_count=int(row[10]) if row[10].strip() else 0,
                    mostly_true_count=int(row[11]) if row[11].strip() else 0,
                    pants_on_fire_count=int(row[12]) if row[12].strip() else 0,
                    context=row[13],
                    split=split,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imported {created} rows into split={split}. "
            f"Skipped empty={skipped_empty}, skipped short={skipped_short}."
        ))