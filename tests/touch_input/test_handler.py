from typing import TYPE_CHECKING

import pytest

from pireader.touch_input import handler
from tests import utils

if TYPE_CHECKING:
    import pytest_mock


@pytest.fixture
def mock_handler(mocker: pytest_mock.MockerFixture) -> handler.TouchHandler:
    """Return a mocked TouchHandler."""
    return handler.TouchHandler(
        driver=mocker.Mock(), engine=mocker.Mock(), resolver=mocker.Mock()
    )


class TestTouchHandlerPollForGesture:
    """TouchHandler poll_for_gesture."""

    def test_poll_calls_resolver(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Calls resolver method."""
        mock_handler._resolver.poll_for_resolved_gestures.return_value = (
            [],
            None,
        )
        mock_handler.poll_for_gesture()

        mock_handler._resolver.poll_for_resolved_gestures.assert_called_once()

    def test_poll_returns_queued_single_touch_gesture(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Return queued single-touch gesture."""
        mock_handler._resolver.poll_for_resolved_gestures.return_value = (
            [],
            None,
        )
        gesture = utils.new_st_gesture()
        mock_handler._queue.put_nowait(gesture)

        result = mock_handler.poll_for_gesture()

        assert mock_handler._queue.empty()
        assert result is gesture

    def test_poll_returns_queued_resolved_single_touch_gesture(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Return queued, resolved single-touch gesture."""
        gesture = utils.new_st_gesture()
        mock_handler._resolver.poll_for_resolved_gestures.return_value = (
            [gesture],
            None,
        )

        result = mock_handler.poll_for_gesture()

        assert mock_handler._queue.empty()
        assert result is gesture

    def test_poll_returns_queued_multi_touch_gesture(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Return queued multi-touch gesture."""
        mock_handler._resolver.poll_for_resolved_gestures.return_value = (
            [],
            None,
        )
        gesture = utils.new_mt_gesture()
        mock_handler._queue.put_nowait(gesture)

        result = mock_handler.poll_for_gesture()

        assert mock_handler._queue.empty()
        assert result is gesture

    def test_poll_returns_queued_resolved_multi_touch_gesture(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Return queued, resolved multi-touch gesture."""
        gesture = utils.new_mt_gesture()
        mock_handler._resolver.poll_for_resolved_gestures.return_value = (
            [],
            gesture,
        )

        result = mock_handler.poll_for_gesture()

        assert mock_handler._queue.empty()
        assert result is gesture


class TestTouchHandlerTouchInterruptHandler:
    """TouchHandler _touch_interrupt_handler."""

    def test_handler_calls_engine_and_resolver(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Calls engine and resolver methods."""
        touch = utils.new_touch(-1, -1, -1)
        single_touch = utils.new_st_gesture()
        multi_touch = utils.new_mt_gesture()
        mock_handler._engine.process_touch_events.return_value = (
            [single_touch],
            multi_touch,
        )

        mock_handler._touch_interrupt_handler([touch])

        mock_handler._engine.process_touch_events.assert_called_once_with(
            [touch]
        )
        mock_handler._resolver.resolve_gestures.assert_called_once_with(
            [single_touch], multi_touch
        )

    def test_handler_queues_single_touch_gestures(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Queue single-touch gestures."""
        gesture1 = utils.new_st_gesture()
        gesture2 = utils.new_st_gesture()
        mock_handler._engine.process_touch_events.return_value = [
            [gesture1, gesture2],
            None,
        ]

        mock_handler._touch_interrupt_handler([])

        assert not mock_handler._queue.empty()
        assert gesture1 in mock_handler._queue.queue
        assert gesture2 in mock_handler._queue.queue

    def test_handler_queues_multi_touch_gesture(
        self, mock_handler: pytest_mock.MockType
    ) -> None:
        """Queue multi-touch gesture."""
        gesture = utils.new_mt_gesture()
        mock_handler._engine.process_touch_events.return_value = [[], gesture]

        mock_handler._touch_interrupt_handler([])

        assert not mock_handler._queue.empty()
        assert gesture in mock_handler._queue.queue
