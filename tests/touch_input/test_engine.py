from collections.abc import Callable

import pytest
import pytest_mock

from pireader.touch_input import engine

EventCreator = Callable[[int], pytest_mock.MockType]


@pytest.fixture
def mock_engine(mocker: pytest_mock.MockerFixture) -> engine.GestureEngine:
    """Return an engine with mocked dependencies."""
    mocker.patch("pireader.touch_input.engine.single")
    mocker.patch("pireader.touch_input.engine.multi")
    return engine.GestureEngine()


@pytest.fixture
def mock_touch_event(mocker: pytest_mock.MockerFixture) -> EventCreator:
    """Return a function that creates a mocked touch event."""

    def creator(id_: int) -> pytest_mock.MockType:
        mock_event = mocker.Mock()
        mock_event.id = id_
        return mock_event

    return creator


class TestGestureEngineProcessTouchEvents:
    """GestureEngine process_touch_events."""

    def test_process_lifted_fingers_and_each_event(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
    ) -> None:
        """Process lifted fingers and each touch event."""
        mock_lifted = mocker.patch.object(
            mock_engine, "_process_lifted_fingers"
        )
        mock_each = mocker.patch.object(
            mock_engine, "_process_each_touch_event"
        )
        touch_events = [mocker.Mock()]

        mock_engine.process_touch_events(touch_events)

        mock_lifted.assert_called_once_with(touch_events)
        mock_each.assert_called_once_with(touch_events)

    def test_process_returns_single_touch_gestures(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
    ) -> None:
        """Two fingers returns two single-touch gestures."""
        mock_first = mocker.Mock()
        mock_second = mocker.Mock()
        mocker.patch.object(mock_engine, "_process_lifted_fingers")
        mocker.patch.object(
            mock_engine,
            "_process_each_touch_event",
            return_value=[mock_first, mock_second],
        )

        result, _ = mock_engine.process_touch_events([])

        assert len(result) == 2
        assert mock_first in result
        assert mock_second in result

    def test_process_returns_multi_touch_gesture(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
    ) -> None:
        """Two fingers returns a multi-touch gesture."""
        mock_first = mocker.Mock()
        mock_second = mocker.Mock()
        mocker.patch.object(mock_engine, "_process_lifted_fingers")
        mocker.patch.object(
            mock_engine,
            "_process_each_touch_event",
            return_value=[mock_first, mock_second],
        )
        mock_machine = mocker.Mock()
        mock_engine._multi_fsm = mock_machine

        _, result = mock_engine.process_touch_events([])

        mock_machine.generate_gesture.assert_called_once_with(
            mock_first, mock_second
        )
        assert result is not None


class TestGestureEngineProcessLiftedFingers:
    """GestureEngine _process_lifted_fingers."""

    def test_process_skips_on_one_finger_lifted(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
        mock_touch_event: pytest_mock.MockType,
    ) -> None:
        """One finger was lifted."""
        event = mock_touch_event(0)
        mock_machine1 = mocker.Mock()
        mock_machine2 = mocker.Mock()
        mock_engine._single_fsms[0] = mock_machine1
        mock_engine._single_fsms[1] = mock_machine2

        result = mock_engine._process_lifted_fingers([event])

        mock_machine1.generate_gesture.assert_not_called()
        mock_machine2.generate_gesture.assert_called_once()
        assert len(result) == 1

    def test_process_skips_on_two_fingers_lifted(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
    ) -> None:
        """Two fingers were lifted."""
        mock_engine._single_fsms[0] = mocker.Mock()
        mock_engine._single_fsms[1] = mocker.Mock()

        result = mock_engine._process_lifted_fingers([])

        mock_engine._single_fsms[0].generate_gesture.assert_called_once()
        mock_engine._single_fsms[1].generate_gesture.assert_called_once()
        assert len(result) == 2

    def test_process_skips_on_two_fingers_lifted_no_gestures_returned(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
    ) -> None:
        """Two fingers were lifted with no gestures returned."""
        machine = mocker.Mock()
        machine.generate_gesture.return_value = None
        mock_engine._single_fsms[0] = machine
        mock_engine._single_fsms[1] = machine

        result = mock_engine._process_lifted_fingers([])

        assert len(result) == 0

    def test_process_skips_on_no_lifted_finger(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
        mock_touch_event: pytest_mock.MockType,
    ) -> None:
        """No finger was lifted."""
        event1 = mock_touch_event(0)
        event2 = mock_touch_event(1)
        mock_engine._single_fsms[0] = mocker.Mock()
        mock_engine._single_fsms[1] = mocker.Mock()

        result = mock_engine._process_lifted_fingers([event1, event2])

        mock_engine._single_fsms[0].generate_gesture.assert_not_called()
        mock_engine._single_fsms[1].generate_gesture.assert_not_called()
        assert len(result) == 0


class TestGestureEngineProcessEachTouchEvent:
    """GestureEngine _process_each_touch_event."""

    def test_process_one_touch_allocates_one_new_machine(
        self, mock_engine: engine.GestureEngine, mock_touch_event: EventCreator
    ) -> None:
        """One touch allocates one single-touch machine."""
        event = mock_touch_event(0)

        mock_engine._process_each_touch_event([event])

        assert len(mock_engine._single_fsms) == 1
        assert 0 in mock_engine._single_fsms

    @pytest.mark.parametrize("event_id", [0, 1])
    def test_process_two_touches_allocates_one_new_machine(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
        mock_touch_event: EventCreator,
        event_id: int,
    ) -> None:
        """Two touches allocates one single-touch machine."""
        event1 = mock_touch_event(0)
        event2 = mock_touch_event(1)
        mock_engine._single_fsms[event_id] = mocker.Mock()

        mock_engine._process_each_touch_event([event1, event2])

        assert len(mock_engine._single_fsms) == 2
        assert 0 in mock_engine._single_fsms
        assert 1 in mock_engine._single_fsms

    def test_process_two_touches_allocates_two_new_machines(
        self, mock_engine: engine.GestureEngine, mock_touch_event: EventCreator
    ) -> None:
        """Two touches allocates two single-touch machines."""
        event1 = mock_touch_event(0)
        event2 = mock_touch_event(1)

        mock_engine._process_each_touch_event([event1, event2])

        assert len(mock_engine._single_fsms) == 2
        assert 0 in mock_engine._single_fsms
        assert 1 in mock_engine._single_fsms

    def test_process_one_touch_returns_no_gesture(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
        mock_touch_event: EventCreator,
    ) -> None:
        """One touch returns no gesture."""
        event = mock_touch_event(0)
        mock_machine = mocker.Mock()
        mock_machine.generate_gesture.return_value = None
        mock_engine._single_fsms[0] = mock_machine

        result = mock_engine._process_each_touch_event([event])

        assert len(result) == 0

    def test_process_one_touch_returns_one_gesture(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
        mock_touch_event: EventCreator,
    ) -> None:
        """One touch returns one gesture."""
        event = mock_touch_event(0)
        mock_engine._single_fsms[0] = mocker.Mock()

        result = mock_engine._process_each_touch_event([event])

        assert len(result) == 1

    def test_process_two_touches_returns_two_gestures(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_engine: engine.GestureEngine,
        mock_touch_event: EventCreator,
    ) -> None:
        """One touch returns no gesture."""
        event1 = mock_touch_event(0)
        event2 = mock_touch_event(1)
        mock_engine._single_fsms[0] = mocker.Mock()
        mock_engine._single_fsms[1] = mocker.Mock()

        result = mock_engine._process_each_touch_event([event1, event2])

        assert len(result) == 2
