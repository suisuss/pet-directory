"""Database change detection worker using PostgreSQL LISTEN/NOTIFY."""

import asyncio
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypedDict

import asyncpg
from jinja2 import Environment, FileSystemLoader, Template
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.pet import Pet
from app.schemas.pet import PetResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ChangeEvent(BaseModel):
    """Model for database change events."""

    operation: str = Field(..., description="Type of operation: INSERT, UPDATE, DELETE")
    table: str = Field(..., description="Table name where change occurred")
    timestamp: str = Field(..., description="Timestamp of the change")
    data: dict[str, Any] = Field(..., description="The record data")


class Stats(TypedDict):
    """Statistics dictionary type."""

    total_events: int
    inserts: int
    updates: int
    deletes: int
    errors: int
    started_at: datetime | None


class ChangeDetector:
    """Detects and processes database changes using PostgreSQL LISTEN/NOTIFY."""

    def __init__(self) -> None:
        """Initialize the change detector."""
        self.connection: asyncpg.Connection | None = None
        self.running = False
        self.stats: Stats = {
            "total_events": 0,
            "inserts": 0,
            "updates": 0,
            "deletes": 0,
            "errors": 0,
            "started_at": None,
        }
        self.loop: asyncio.AbstractEventLoop | None = None

    async def connect(self) -> None:
        """Establish connection to the database."""
        try:
            # Parse the DATABASE_URL and use direct asyncpg connection
            # Convert from postgresql:// or postgresql+asyncpg:// to asyncpg format
            db_url = settings.DATABASE_URL
            if db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            elif db_url.startswith("postgres://"):
                # Some systems use postgres:// instead of postgresql://
                db_url = db_url.replace("postgres://", "postgresql://")

            self.connection = await asyncpg.connect(db_url)
            logger.info("Connected to database for change detection")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")

    async def generate_report(self) -> None:
        """Generate and print pet report to stdout."""
        async with AsyncSessionLocal() as session:
            try:
                # Query all pets from database
                result = await session.execute(
                    select(Pet).order_by(Pet.pet_type, Pet.name)
                )
                pets: list[Pet] = list(result.scalars().all())

                # Convert to Pydantic models
                pet_responses: list[PetResponse] = [
                    PetResponse.model_validate(pet) for pet in pets
                ]

                # Group pets by type
                pets_by_type: defaultdict[str, list[PetResponse]] = defaultdict(list)
                for pet in pet_responses:
                    pets_by_type[pet.pet_type].append(pet)

                # Count pets by type
                pet_type_counts: dict[str, int] = {
                    pet_type: len(pets_list)
                    for pet_type, pets_list in pets_by_type.items()
                }

                # Setup Jinja2 template
                template_dir: Path = Path(__file__).parent.parent / "templates"
                env: Environment = Environment(
                    loader=FileSystemLoader(str(template_dir)),
                    autoescape=True,
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

                # Print to stdout with clear separator
                print("\n" + "=" * 60)
                print("📊 PET DIRECTORY REPORT (Triggered by Database Change)")
                print("=" * 60)
                print(report)
                print("=" * 60 + "\n")
                sys.stdout.flush()

            except SQLAlchemyError as e:
                logger.error(f"Database error generating report: {e}")
            except Exception as e:
                logger.error(f"Unexpected error generating report: {e}")

    def process_notification(
        self, connection: asyncpg.Connection, pid: int, channel: str, payload: str
    ) -> None:
        """Process a database change notification.

        Args:
            connection: The connection that received the notification
            pid: Process ID of the notifying PostgreSQL backend
            channel: Notification channel name
            payload: JSON payload containing change details
        """
        try:
            # Parse the JSON payload
            data = json.loads(payload)
            event = ChangeEvent(**data)

            # Update statistics
            self.stats["total_events"] += 1
            operation_lower = event.operation.lower()
            if operation_lower == "insert":
                self.stats["inserts"] += 1
            elif operation_lower == "update":
                self.stats["updates"] += 1
            elif operation_lower == "delete":
                self.stats["deletes"] += 1

            # Log the change
            logger.info(
                f"📊 Database Change Detected:\n"
                f"  Operation: {event.operation}\n"
                f"  Table: {event.table}\n"
                f"  Timestamp: {event.timestamp}\n"
                f"  Record ID: {event.data.get('id', 'N/A')}"
            )

            # Process based on operation type (sync context, so we just log)
            if event.operation == "INSERT":
                pet_name = event.data.get("name", "Unknown")
                pet_type = event.data.get("pet_type", "Unknown")
                logger.info(f"🆕 New pet added: {pet_name} ({pet_type})")
            elif event.operation == "UPDATE":
                pet_id = event.data.get("id")
                pet_name = event.data.get("name", "Unknown")
                logger.info(f"✏️  Pet updated: ID {pet_id} - {pet_name}")
            elif event.operation == "DELETE":
                pet_id = event.data.get("id")
                pet_name = event.data.get("name", "Unknown")
                logger.info(f"🗑️  Pet deleted: ID {pet_id} - {pet_name}")

            # Schedule report generation in the async context
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.generate_report(), self.loop)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse notification payload: {e}")
            self.stats["errors"] += 1
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            self.stats["errors"] += 1

    async def listen(self) -> None:
        """Start listening for database changes."""
        if not self.connection:
            await self.connect()

        # Ensure connection is established
        assert self.connection is not None, "Failed to establish database connection"

        # Store the event loop for use in callbacks
        self.loop = asyncio.get_event_loop()

        # Add listener for the pet_changes channel
        await self.connection.add_listener("pet_changes", self.process_notification)
        logger.info("Started listening for pet_changes notifications")

        self.running = True
        self.stats["started_at"] = datetime.now()

        # Generate initial report
        logger.info("Generating initial pet report...")
        await self.generate_report()

        # Keep the worker running
        try:
            while self.running:
                await asyncio.sleep(1)

                # Periodically log statistics
                if (
                    self.stats["total_events"] > 0
                    and self.stats["total_events"] % 10 == 0
                ):
                    await self.log_statistics()

        except asyncio.CancelledError:
            logger.info("Change detector cancelled")
        finally:
            if self.connection:
                await self.connection.remove_listener(
                    "pet_changes", self.process_notification
                )
            await self.disconnect()

    async def log_statistics(self) -> None:
        """Log current statistics."""
        uptime: timedelta | str = (
            datetime.now() - self.stats["started_at"]
            if self.stats["started_at"] is not None
            else "N/A"
        )
        logger.info(
            f"📈 Change Detection Statistics:\n"
            f"  Total Events: {self.stats['total_events']}\n"
            f"  Inserts: {self.stats['inserts']}\n"
            f"  Updates: {self.stats['updates']}\n"
            f"  Deletes: {self.stats['deletes']}\n"
            f"  Errors: {self.stats['errors']}\n"
            f"  Uptime: {uptime}"
        )

    def stop(self) -> None:
        """Stop the change detector."""
        self.running = False
        logger.info("Stopping change detector...")


async def main() -> None:
    """Main entry point for the change detector worker."""
    detector = ChangeDetector()

    try:
        logger.info("🚀 Starting Database Change Detection Worker")
        await detector.listen()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
    finally:
        detector.stop()
        await detector.log_statistics()


if __name__ == "__main__":
    asyncio.run(main())
