import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from claims.models import Claim


class Command(BaseCommand):
    help = "Import LIAR dataset from data/raw into the Claim model"

    def handle(self, *args, **kwargs):
        # This points to the project root: credibility-intelligence-api/
        project_root = Path(__file__).resolve().parents[4]
        data_dir = project_root / "data" / "raw"

        files = [
            ("train.tsv", "train"),
            ("valid.tsv", "valid"),
            ("test.tsv", "test"),
        ]

        created_count = 0
        updated_count = 0

        for filename, split_name in files:
            file_path = data_dir / filename

            if not file_path.exists():
                self.stdout.write(self.style.WARNING(f"Missing file: {file_path}"))
                continue

            self.stdout.write(f"Importing {filename}...")

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")

                for row in reader:
                    if len(row) < 14:
                        continue

                    liar_id = row[0].strip()

                    defaults = {
                        "label": row[1].strip(),
                        "statement": row[2].strip(),
                        "subjects": row[3].strip(),
                        "speaker": row[4].strip(),
                        "speaker_job_title": row[5].strip(),
                        "state": row[6].strip(),
                        "party": row[7].strip(),
                        "barely_true_count": int(row[8] or 0),
                        "false_count": int(row[9] or 0),
                        "half_true_count": int(row[10] or 0),
                        "mostly_true_count": int(row[11] or 0),
                        "pants_on_fire_count": int(row[12] or 0),
                        "context": row[13].strip(),
                        "split": split_name,
                    }

                    _, created = Claim.objects.update_or_create(
                        liar_id=liar_id,
                        defaults=defaults,
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created: {created_count}, Updated: {updated_count}"
            )
        )