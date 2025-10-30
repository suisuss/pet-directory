"""Background worker for generating pet reports."""

import asyncio
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.pet import Pet
from app.schemas.pet import PetResponse


async def generate_report() -> None:
    """
    Generate and print pet report to stdout.

    Fetches all pets from the database, groups them by type,
    and renders a formatted report using Jinja2 template.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Query all pets from database
            result = await session.execute(select(Pet).order_by(Pet.pet_type, Pet.name))
            pets: list[Pet] = list(result.scalars().all())

            # Convert to Pydantic models for consistency
            pet_responses: list[PetResponse] = [
                PetResponse.model_validate(pet) for pet in pets
            ]

            # Group pets by type
            pets_by_type: defaultdict[str, list[PetResponse]] = defaultdict(list)
            for pet in pet_responses:
                pets_by_type[pet.pet_type].append(pet)

            # Count pets by type
            pet_type_counts: dict[str, int] = {
                pet_type: len(pets_list) for pet_type, pets_list in pets_by_type.items()
            }

            # Setup Jinja2 template
            template_dir: Path = Path(__file__).parent.parent / "templates"
            env: Environment = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=True,  # Enable autoescape for security
                trim_blocks=True,
                lstrip_blocks=True,
            )
            template: Template = env.get_template("pet_report.j2")

            # Render report
            report: str = template.render(
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                total_pets=len(pet_responses),
                pets=pet_responses,
                pets_by_type=dict(pets_by_type),
                pet_type_counts=pet_type_counts,
            )

            # Print to stdout
            print(report)
            sys.stdout.flush()

        except SQLAlchemyError as e:
            print(f"Database error generating report: {e}", file=sys.stderr)
            sys.stderr.flush()
        except Exception as e:
            print(f"Unexpected error generating report: {e}", file=sys.stderr)
            sys.stderr.flush()


async def main() -> None:
    """
    Main worker loop - generate report periodically.

    Generates reports at intervals specified in configuration.
    Handles graceful shutdown on keyboard interrupt.
    """
    interval: int = settings.REPORT_INTERVAL_SECONDS

    print("Pet Report Worker Started", file=sys.stdout)
    print(f"Will generate reports every {interval} seconds...\n", file=sys.stdout)
    sys.stdout.flush()

    while True:
        try:
            await generate_report()
            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\nWorker shutting down gracefully...", file=sys.stdout)
            break
        except asyncio.CancelledError:
            print("\nWorker task cancelled.", file=sys.stdout)
            break
        except Exception as e:
            print(f"Unexpected error in worker loop: {e}", file=sys.stderr)
            sys.stderr.flush()
            # Continue after error with same interval
            await asyncio.sleep(interval)


def run_worker() -> None:
    """
    Entry point for running the worker.

    Sets up event loop and runs the main worker coroutine.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker stopped by user.", file=sys.stdout)
    except Exception as e:
        print(f"Fatal error in worker: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_worker()
