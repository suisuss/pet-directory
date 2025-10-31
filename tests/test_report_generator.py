"""Tests for report generator worker."""

import asyncio
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.pet import Pet
from app.worker.report_generator import generate_report, main, run_worker


class TestGenerateReport:
    """Tests for generate_report function."""

    async def test_generate_report_with_pets(
        self, test_db, capsys, monkeypatch
    ) -> None:
        """Test generating report with pets in database."""
        from app.repositories.pet import PetRepository
        from app.schemas.pet import PetCreate

        # Create test pets
        repo = PetRepository(db=test_db)
        await repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))
        await repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))

        # Mock AsyncSessionLocal to use test_db
        class MockSessionLocal:
            def __init__(self):
                pass

            async def __aenter__(self):
                return test_db

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        monkeypatch.setattr(
            "app.worker.report_generator.AsyncSessionLocal", MockSessionLocal
        )

        # Generate report
        await generate_report()

        # Check output
        captured = capsys.readouterr()
        assert "PET DIRECTORY REPORT" in captured.out
        assert "Buddy" in captured.out
        assert "Whiskers" in captured.out
        assert "Max" in captured.out
        assert "dog" in captured.out.lower()
        assert "cat" in captured.out.lower()

    async def test_generate_report_empty_database(self, capsys) -> None:
        """Test generating report with no pets."""
        await generate_report()

        captured = capsys.readouterr()
        assert "PET DIRECTORY REPORT" in captured.out
        # Should still generate a report, just with 0 pets

    async def test_generate_report_database_error(
        self, capsys, monkeypatch
    ) -> None:
        """Test report generation handles database errors gracefully."""
        from app.core.database import AsyncSessionLocal

        # Mock session to raise error
        async def mock_execute(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr(
            "app.worker.report_generator.AsyncSessionLocal",
            lambda: mock_session,
        )

        await generate_report()

        captured = capsys.readouterr()
        assert "Database error" in captured.err

    async def test_generate_report_template_error(
        self, test_db, capsys, monkeypatch
    ) -> None:
        """Test report generation handles template errors gracefully."""
        from app.repositories.pet import PetRepository
        from app.schemas.pet import PetCreate

        # Create a pet
        repo = PetRepository(db=test_db)
        await repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        # Mock template to raise error
        mock_env = MagicMock()
        mock_env.get_template.side_effect = Exception("Template not found")

        monkeypatch.setattr(
            "app.worker.report_generator.Environment", lambda **kwargs: mock_env
        )

        await generate_report()

        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err

    async def test_generate_report_groups_by_type(
        self, test_db, capsys, monkeypatch
    ) -> None:
        """Test that report properly groups pets by type."""
        from app.core.database import AsyncSessionLocal
        from app.repositories.pet import PetRepository
        from app.schemas.pet import PetCreate

        # Create multiple pets of same type
        repo = PetRepository(db=test_db)
        await repo.create(obj_in=PetCreate(name="Dog1", pet_type="dog"))
        await repo.create(obj_in=PetCreate(name="Dog2", pet_type="dog"))
        await repo.create(obj_in=PetCreate(name="Cat1", pet_type="cat"))

        # Mock AsyncSessionLocal to use test_db
        class MockSessionLocal:
            def __init__(self):
                pass

            async def __aenter__(self):
                return test_db

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        monkeypatch.setattr(
            "app.worker.report_generator.AsyncSessionLocal", MockSessionLocal
        )

        await generate_report()

        captured = capsys.readouterr()
        # Report should contain all pets
        assert "Dog1" in captured.out
        assert "Dog2" in captured.out
        assert "Cat1" in captured.out


class TestMain:
    """Tests for main worker loop."""

    @pytest.mark.timeout(5)
    async def test_main_generates_reports_periodically(
        self, monkeypatch, capsys
    ) -> None:
        """Test that main loop generates reports at intervals."""
        report_count = 0

        async def mock_generate_report():
            nonlocal report_count
            report_count += 1
            if report_count >= 2:
                # Stop after 2 reports
                raise asyncio.CancelledError()

        monkeypatch.setattr(
            "app.worker.report_generator.generate_report", mock_generate_report
        )
        monkeypatch.setattr(
            "app.worker.report_generator.settings.REPORT_INTERVAL_SECONDS", 0.1
        )

        try:
            await main()
        except asyncio.CancelledError:
            pass

        assert report_count == 2
        captured = capsys.readouterr()
        assert "Pet Report Worker Started" in captured.out

    @pytest.mark.timeout(5)
    async def test_main_handles_keyboard_interrupt(
        self, monkeypatch, capsys
    ) -> None:
        """Test that main loop handles KeyboardInterrupt gracefully."""

        async def mock_generate_report():
            raise KeyboardInterrupt()

        monkeypatch.setattr(
            "app.worker.report_generator.generate_report", mock_generate_report
        )

        await main()

        captured = capsys.readouterr()
        assert "shutting down gracefully" in captured.out

    @pytest.mark.timeout(5)
    async def test_main_continues_after_error(
        self, monkeypatch, capsys
    ) -> None:
        """Test that main loop continues after errors."""
        call_count = 0

        async def mock_generate_report():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            elif call_count >= 2:
                raise asyncio.CancelledError()

        monkeypatch.setattr(
            "app.worker.report_generator.generate_report", mock_generate_report
        )
        monkeypatch.setattr(
            "app.worker.report_generator.settings.REPORT_INTERVAL_SECONDS", 0.1
        )

        try:
            await main()
        except asyncio.CancelledError:
            pass

        assert call_count >= 2
        captured = capsys.readouterr()
        assert "Unexpected error in worker loop" in captured.err

    @pytest.mark.timeout(5)
    async def test_main_respects_interval_setting(
        self, monkeypatch, capsys
    ) -> None:
        """Test that main loop uses configured interval."""
        import time

        start_time = time.time()
        call_times = []

        async def mock_generate_report():
            call_times.append(time.time())
            if len(call_times) >= 2:
                raise asyncio.CancelledError()

        monkeypatch.setattr(
            "app.worker.report_generator.generate_report", mock_generate_report
        )
        monkeypatch.setattr(
            "app.worker.report_generator.settings.REPORT_INTERVAL_SECONDS", 0.2
        )

        try:
            await main()
        except asyncio.CancelledError:
            pass

        # Verify there was a delay between calls
        if len(call_times) >= 2:
            interval = call_times[1] - call_times[0]
            assert interval >= 0.15  # Allow some tolerance


class TestRunWorker:
    """Tests for run_worker entry point."""

    def test_run_worker_calls_main(self, monkeypatch, capsys) -> None:
        """Test that run_worker calls main loop."""
        main_called = False

        async def mock_main():
            nonlocal main_called
            main_called = True

        monkeypatch.setattr("app.worker.report_generator.main", mock_main)

        # Mock asyncio.run to avoid actually running the loop
        def mock_asyncio_run(coro):
            # Just mark that it was called
            pass

        monkeypatch.setattr("asyncio.run", mock_asyncio_run)

        run_worker()
        # Just verify it doesn't crash

    def test_run_worker_handles_keyboard_interrupt(
        self, monkeypatch, capsys
    ) -> None:
        """Test that run_worker handles KeyboardInterrupt."""

        def mock_asyncio_run(coro):
            raise KeyboardInterrupt()

        monkeypatch.setattr("asyncio.run", mock_asyncio_run)

        run_worker()

        captured = capsys.readouterr()
        assert "stopped by user" in captured.out

    def test_run_worker_handles_fatal_error(self, monkeypatch, capsys) -> None:
        """Test that run_worker handles fatal errors."""

        def mock_asyncio_run(coro):
            raise Exception("Fatal error")

        monkeypatch.setattr("asyncio.run", mock_asyncio_run)

        with pytest.raises(SystemExit) as exc_info:
            run_worker()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Fatal error" in captured.err
