import asyncio
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.pet import Pet
from app.schemas.pet import PetResponse


async def generate_report():
    """Generate and print pet report to stdout."""
    async with AsyncSessionLocal() as session:
        try:
            # Query all pets from database
            result = await session.execute(
                select(Pet).order_by(Pet.pet_type, Pet.name)
            )
            pets = result.scalars().all()
            
            # Convert to Pydantic models for consistency
            pet_responses = [PetResponse.model_validate(pet) for pet in pets]
            
            # Group pets by type
            pets_by_type = defaultdict(list)
            for pet in pet_responses:
                pets_by_type[pet.pet_type].append(pet)
            
            # Count pets by type
            pet_type_counts = {
                pet_type: len(pets_list) 
                for pet_type, pets_list in pets_by_type.items()
            }
            
            # Setup Jinja2 template
            template_dir = Path(__file__).parent.parent / "templates"
            env = Environment(loader=FileSystemLoader(str(template_dir)))
            template = env.get_template("pet_report.j2")
            
            # Render report
            report = template.render(
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                total_pets=len(pet_responses),
                pets=pet_responses,  # Add the full pets list
                pets_by_type=dict(pets_by_type),
                pet_type_counts=pet_type_counts
            )
            
            # Print to stdout
            print(report)
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Error generating report: {e}", file=sys.stderr)
            sys.stderr.flush()


async def main():
    """Main worker loop - generate report every minute."""
    print("Pet Report Worker Started", file=sys.stdout)
    print("Will generate reports every 60 seconds...\n", file=sys.stdout)
    sys.stdout.flush()
    
    while True:
        try:
            await generate_report()
            await asyncio.sleep(60)  # Wait 60 seconds
        except KeyboardInterrupt:
            print("\nWorker shutting down...", file=sys.stdout)
            break
        except Exception as e:
            print(f"Unexpected error in worker loop: {e}", file=sys.stderr)
            await asyncio.sleep(60)  # Continue after error


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker stopped.", file=sys.stdout)