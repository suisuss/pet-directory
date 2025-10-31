"""Tests for change detector worker."""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.worker.change_detector import ChangeDetector, ChangeEvent, Stats, main


class TestChangeEvent:
    """Tests for ChangeEvent model."""

    def test_change_event_creation(self) -> None:
        """Test creating a ChangeEvent."""
        event = ChangeEvent(
            operation="INSERT",
            table="pets",
            timestamp="2025-10-31T12:00:00",
            data={"id": 1, "name": "Buddy", "pet_type": "dog"},
        )

        assert event.operation == "INSERT"
        assert event.table == "pets"
        assert event.timestamp == "2025-10-31T12:00:00"
        assert event.data["name"] == "Buddy"

    def test_change_event_validation(self) -> None:
        """Test ChangeEvent validates required fields."""
        with pytest.raises(Exception):
            ChangeEvent(operation="INSERT")  # Missing required fields


class TestChangeDetector:
    """Tests for ChangeDetector class."""

    def test_change_detector_initialization(self) -> None:
        """Test ChangeDetector initializes with correct defaults."""
        detector = ChangeDetector()

        assert detector.connection is None
        assert detector.running is False
        assert detector.stats["total_events"] == 0
        assert detector.stats["inserts"] == 0
        assert detector.stats["updates"] == 0
        assert detector.stats["deletes"] == 0
        assert detector.stats["errors"] == 0
        assert detector.stats["started_at"] is None
        assert detector.loop is None

    async def test_connect_success(self, monkeypatch) -> None:
        """Test successful database connection."""
        mock_connection = AsyncMock()

        async def mock_connect(url):
            return mock_connection

        monkeypatch.setattr("asyncpg.connect", mock_connect)

        detector = ChangeDetector()
        await detector.connect()

        assert detector.connection is not None

    async def test_connect_failure(self, monkeypatch, capsys) -> None:
        """Test connection failure handling."""

        async def mock_connect_fail(url):
            raise Exception("Connection failed")

        monkeypatch.setattr("asyncpg.connect", mock_connect_fail)

        detector = ChangeDetector()
        with pytest.raises(Exception):
            await detector.connect()

    async def test_disconnect(self) -> None:
        """Test disconnecting from database."""
        detector = ChangeDetector()
        mock_connection = AsyncMock()
        detector.connection = mock_connection

        await detector.disconnect()

        mock_connection.close.assert_called_once()

    async def test_disconnect_no_connection(self) -> None:
        """Test disconnect when no connection exists."""
        detector = ChangeDetector()
        await detector.disconnect()  # Should not raise

    async def test_generate_report(self, test_db, capsys, monkeypatch) -> None:
        """Test report generation."""
        from app.repositories.pet import PetRepository
        from app.schemas.pet import PetCreate

        # Create test pets
        repo = PetRepository(db=test_db)
        await repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        # Mock AsyncSessionLocal to use test_db
        class MockSessionLocal:
            def __init__(self):
                pass

            async def __aenter__(self):
                return test_db

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        monkeypatch.setattr(
            "app.worker.change_detector.AsyncSessionLocal", MockSessionLocal
        )

        detector = ChangeDetector()
        await detector.generate_report()

        captured = capsys.readouterr()
        assert "PET DIRECTORY REPORT" in captured.out
        assert "Buddy" in captured.out

    async def test_generate_report_database_error(self, monkeypatch, capsys) -> None:
        """Test report generation handles database errors."""
        detector = ChangeDetector()

        # Mock AsyncSessionLocal to raise error
        mock_session = AsyncMock()
        mock_session.execute.side_effect = SQLAlchemyError("DB Error")
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(
            "app.worker.change_detector.AsyncSessionLocal", lambda: mock_session
        )

        await detector.generate_report()
        # Should not raise, just log error

    def test_process_notification_insert(self, capsys) -> None:
        """Test processing INSERT notification."""
        detector = ChangeDetector()
        detector.loop = asyncio.get_event_loop()

        payload = json.dumps(
            {
                "operation": "INSERT",
                "table": "pets",
                "timestamp": "2025-10-31T12:00:00",
                "data": {"id": 1, "name": "Buddy", "pet_type": "dog"},
            }
        )

        mock_connection = MagicMock()
        detector.process_notification(mock_connection, 123, "pet_changes", payload)

        assert detector.stats["total_events"] == 1
        assert detector.stats["inserts"] == 1
        assert detector.stats["updates"] == 0
        assert detector.stats["deletes"] == 0

    def test_process_notification_update(self) -> None:
        """Test processing UPDATE notification."""
        detector = ChangeDetector()
        detector.loop = asyncio.get_event_loop()

        payload = json.dumps(
            {
                "operation": "UPDATE",
                "table": "pets",
                "timestamp": "2025-10-31T12:00:00",
                "data": {"id": 1, "name": "Updated", "pet_type": "dog"},
            }
        )

        mock_connection = MagicMock()
        detector.process_notification(mock_connection, 123, "pet_changes", payload)

        assert detector.stats["total_events"] == 1
        assert detector.stats["inserts"] == 0
        assert detector.stats["updates"] == 1
        assert detector.stats["deletes"] == 0

    def test_process_notification_delete(self) -> None:
        """Test processing DELETE notification."""
        detector = ChangeDetector()
        detector.loop = asyncio.get_event_loop()

        payload = json.dumps(
            {
                "operation": "DELETE",
                "table": "pets",
                "timestamp": "2025-10-31T12:00:00",
                "data": {"id": 1, "name": "Deleted", "pet_type": "dog"},
            }
        )

        mock_connection = MagicMock()
        detector.process_notification(mock_connection, 123, "pet_changes", payload)

        assert detector.stats["total_events"] == 1
        assert detector.stats["inserts"] == 0
        assert detector.stats["updates"] == 0
        assert detector.stats["deletes"] == 1

    def test_process_notification_invalid_json(self, capsys) -> None:
        """Test processing notification with invalid JSON."""
        detector = ChangeDetector()

        mock_connection = MagicMock()
        detector.process_notification(
            mock_connection, 123, "pet_changes", "invalid json"
        )

        assert detector.stats["errors"] == 1

    def test_process_notification_invalid_event(self) -> None:
        """Test processing notification with invalid event data."""
        detector = ChangeDetector()

        # Missing required fields
        payload = json.dumps({"operation": "INSERT"})

        mock_connection = MagicMock()
        detector.process_notification(mock_connection, 123, "pet_changes", payload)

        assert detector.stats["errors"] == 1

    @pytest.mark.timeout(5)
    async def test_listen_starts_and_stops(self, monkeypatch) -> None:
        """Test that listen starts and can be stopped."""
        detector = ChangeDetector()

        mock_connection = AsyncMock()
        mock_connection.add_listener = AsyncMock()
        mock_connection.remove_listener = AsyncMock()

        async def mock_connect(url):
            return mock_connection

        monkeypatch.setattr("asyncpg.connect", mock_connect)

        # Make listen exit after short time
        async def mock_sleep(seconds):
            detector.running = False

        monkeypatch.setattr("asyncio.sleep", mock_sleep)

        await detector.listen()

        assert mock_connection.add_listener.called
        assert detector.stats["started_at"] is not None

    @pytest.mark.timeout(5)
    async def test_listen_handles_cancellation(self, monkeypatch) -> None:
        """Test that listen handles cancellation gracefully."""
        detector = ChangeDetector()

        mock_connection = AsyncMock()

        async def mock_connect(url):
            return mock_connection

        monkeypatch.setattr("asyncpg.connect", mock_connect)

        # Make sleep raise CancelledError
        async def mock_sleep(seconds):
            raise asyncio.CancelledError()

        monkeypatch.setattr("asyncio.sleep", mock_sleep)

        await detector.listen()

        # Should complete without raising

    async def test_log_statistics(self, caplog) -> None:
        """Test logging statistics."""
        import logging

        caplog.set_level(logging.INFO)
        detector = ChangeDetector()
        detector.stats["total_events"] = 10
        detector.stats["inserts"] = 5
        detector.stats["updates"] = 3
        detector.stats["deletes"] = 2
        detector.stats["errors"] = 0
        detector.stats["started_at"] = datetime.now()

        await detector.log_statistics()

        log_text = caplog.text
        assert "Change Detection Statistics" in log_text
        assert "Total Events: 10" in log_text
        assert "Inserts: 5" in log_text
        assert "Updates: 3" in log_text
        assert "Deletes: 2" in log_text

    async def test_log_statistics_no_start_time(self, caplog) -> None:
        """Test logging statistics when started_at is None."""
        import logging

        caplog.set_level(logging.INFO)
        detector = ChangeDetector()
        detector.stats["total_events"] = 5

        await detector.log_statistics()

        log_text = caplog.text
        assert "Uptime: N/A" in log_text

    def test_stop(self) -> None:
        """Test stopping the detector."""
        detector = ChangeDetector()
        detector.running = True

        detector.stop()

        assert detector.running is False

    @pytest.mark.timeout(5)
    async def test_periodic_statistics_logging(self, monkeypatch) -> None:
        """Test that statistics are logged periodically."""
        detector = ChangeDetector()
        detector.stats["total_events"] = 10  # Will trigger logging

        mock_connection = AsyncMock()

        async def mock_connect(url):
            return mock_connection

        monkeypatch.setattr("asyncpg.connect", mock_connect)

        sleep_count = 0

        async def mock_sleep(seconds):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count >= 2:
                detector.running = False

        monkeypatch.setattr("asyncio.sleep", mock_sleep)

        log_stats_called = False
        original_log_stats = detector.log_statistics

        async def mock_log_statistics():
            nonlocal log_stats_called
            log_stats_called = True
            await original_log_stats()

        detector.log_statistics = mock_log_statistics

        await detector.listen()

        assert log_stats_called


class TestMain:
    """Tests for main entry point."""

    @pytest.mark.timeout(5)
    async def test_main_starts_detector(self, monkeypatch, caplog) -> None:
        """Test that main starts the detector."""
        import logging

        caplog.set_level(logging.INFO)
        listen_called = False

        async def mock_listen(self):
            nonlocal listen_called
            listen_called = True

        monkeypatch.setattr(ChangeDetector, "listen", mock_listen)

        await main()

        assert listen_called
        log_text = caplog.text
        assert "Starting Database Change Detection Worker" in log_text

    @pytest.mark.timeout(5)
    async def test_main_handles_keyboard_interrupt(self, monkeypatch, caplog) -> None:
        """Test that main handles KeyboardInterrupt."""
        import logging

        caplog.set_level(logging.INFO)

        async def mock_listen(self):
            raise KeyboardInterrupt()

        monkeypatch.setattr(ChangeDetector, "listen", mock_listen)

        await main()

        log_text = caplog.text
        assert "Received interrupt signal" in log_text

    @pytest.mark.timeout(5)
    async def test_main_handles_errors(self, monkeypatch, caplog) -> None:
        """Test that main handles errors gracefully."""
        import logging

        caplog.set_level(logging.ERROR)

        async def mock_listen(self):
            raise Exception("Test error")

        monkeypatch.setattr(ChangeDetector, "listen", mock_listen)

        await main()

        log_text = caplog.text
        assert "Worker failed" in log_text
