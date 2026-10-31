from typing import TYPE_CHECKING
from unittest import mock

import pytest

from pireader import config
from pireader.common import enums, models
from pireader.touch_input import resolver
from tests import utils

if TYPE_CHECKING:
    import pytest_mock


@pytest.fixture
def mock_time(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """Mock time."""
    return mocker.patch("pireader.touch_input.resolver.time")


class TestGestureResolverPollForResolvedGestures:
    """GestureResolver poll_for_resolved_gestures."""

    test_config = config.GestureConfig(
        slow_tap=config.SlowTapConfig(max_sec=20)
    )

    def test_poll_skips_not_yet_expired_single_touch_fast_tap(
        self, mock_time: pytest_mock.MockType
    ) -> None:
        """Skip not yet expired single-touch FAST TAP gesture."""
        mock_time.time.return_value = 40
        processor = resolver.GestureResolver(config=self.test_config)
        gesture = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(-1, -1, 21, 1)
        )
        processor._active_single_touches[1] = {
            "gesture": gesture,
            "tap_count": 1,
        }

        result, _ = processor.poll_for_resolved_gestures()

        assert 1 in processor._active_single_touches
        assert len(result) == 0

    def test_poll_skips_not_yet_expired_two_single_touch_fast_taps(
        self, mock_time: pytest_mock.MockType
    ) -> None:
        """Skip not yet expired two single-touch FAST TAP gestures."""
        mock_time.time.return_value = 40
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(-1, -1, 21, 1)
        )
        gesture2 = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(-1, -1, 21, 2)
        )
        processor._active_single_touches[1] = {
            "gesture": gesture1,
            "tap_count": 1,
        }
        processor._active_single_touches[2] = {
            "gesture": gesture2,
            "tap_count": 1,
        }

        result, _ = processor.poll_for_resolved_gestures()

        assert 1 in processor._active_single_touches
        assert 2 in processor._active_single_touches
        assert len(result) == 0

    def test_poll_resolves_single_touch_fast_tap(
        self, mock_time: pytest_mock.MockType
    ) -> None:
        """Resolve expired single-touch FAST TAP gesture into a SLOW TAP."""
        mock_time.time.return_value = 40
        processor = resolver.GestureResolver(config=self.test_config)
        gesture = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(-1, -1, 20, 1)
        )
        processor._active_single_touches[1] = {
            "gesture": gesture,
            "tap_count": 2,
        }

        result, _ = processor.poll_for_resolved_gestures()

        assert len(processor._active_single_touches) == 0
        assert len(result) == 1
        assert result[0].state is enums.SingleTouchState.SLOW_TAP
        assert result[0].tap_count == 2

    def test_poll_resolves_two_single_touch_fast_taps(
        self, mock_time: pytest_mock.MockType
    ) -> None:
        """Resolve 2 expired single-touch FAST TAP gestures into SLOW TAPs."""
        mock_time.time.return_value = 40
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(-1, -1, 20, 1)
        )
        gesture2 = utils.new_st_gesture(
            enums.SingleTouchState.FAST_TAP, end=(-1, -1, 20, 1)
        )
        processor._active_single_touches[1] = {
            "gesture": gesture1,
            "tap_count": 2,
        }
        processor._active_single_touches[2] = {
            "gesture": gesture2,
            "tap_count": 3,
        }

        result, _ = processor.poll_for_resolved_gestures()

        assert len(processor._active_single_touches) == 0
        assert len(result) == 2
        assert result[0].state is enums.SingleTouchState.SLOW_TAP
        assert result[0].tap_count == 2
        assert result[1].state is enums.SingleTouchState.SLOW_TAP
        assert result[1].tap_count == 3

    @pytest.mark.parametrize(
        ("first_timestamp", "second_timestamp"),
        [
            (0, 21),  # Selects first
            (21, 0),  # Selects second
            (21, 21),  # Selects either
        ],
    )
    def test_poll_skips_not_yet_expired_multi_touch_fast_tap(
        self,
        mock_time: pytest_mock.MockType,
        first_timestamp: int,
        second_timestamp: int,
    ) -> None:
        """Skip not yet expired multi-touch FAST TAP gesture."""
        mock_time.time.return_value = 40
        processor = resolver.GestureResolver(config=self.test_config)
        gesture = utils.new_mt_gesture(
            enums.MultiTouchState.FAST_TAP,
            first_end=(-1, -1, first_timestamp, 1),
            second_end=(-1, -1, second_timestamp, 1),
        )
        processor._active_multi_touch = {"gesture": gesture, "tap_count": 1}

        _, result = processor.poll_for_resolved_gestures()

        assert processor._active_multi_touch["gesture"] is gesture
        assert processor._active_multi_touch["tap_count"] == 1
        assert result is None

    def test_poll_resolves_multi_touch_fast_tap(
        self, mock_time: pytest_mock.MockType
    ) -> None:
        """Resolve expired multi-touch FAST TAP gesture into a SLOW TAP."""
        mock_time.time.return_value = 40
        processor = resolver.GestureResolver(config=self.test_config)
        gesture = utils.new_mt_gesture(
            enums.MultiTouchState.FAST_TAP,
            first_end=(-1, -1, 20, 1),
            second_end=(-1, -1, 20, 1),
        )
        processor._active_multi_touch = {"gesture": gesture, "tap_count": 2}

        _, result = processor.poll_for_resolved_gestures()

        assert processor._active_multi_touch["gesture"] is None
        assert processor._active_multi_touch["tap_count"] == 1
        assert isinstance(result, models.MultiTouchGesture)
        assert result.state == enums.MultiTouchState.SLOW_TAP
        assert result.tap_count == 2


class TestGestureResolverResolveGestures:
    """GestureResolver resolve_gestures."""

    def test_resolve_single_touch_fast_tap(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Process single-touch FAST TAP gestures."""
        processor = resolver.GestureResolver()
        gesture1 = utils.new_st_gesture(enums.SingleTouchState.FAST_TAP)
        gesture2 = utils.new_st_gesture(enums.SingleTouchState.FAST_TAP)
        mock_process = mocker.patch.object(
            processor, "_process_single_touch_fast_tap"
        )

        processor.resolve_gestures([gesture1, gesture2], None)

        expected = [mock.call(gesture1), mock.call(gesture2)]
        mock_process.assert_has_calls(expected)

    def test_resolve_multi_touch_fast_tap(
        self, mocker: pytest_mock.MockerFixture
    ) -> None:
        """Process multi-touch FAST TAP gesture."""
        processor = resolver.GestureResolver()
        gesture = utils.new_mt_gesture(enums.MultiTouchState.FAST_TAP)
        mock_process = mocker.patch.object(
            processor, "_process_multi_touch_fast_tap"
        )

        processor.resolve_gestures([], gesture)

        mock_process.assert_called_once_with(gesture)


class TestGestureResolverProcessSingleTouchFastTap:
    """GestureResolver _process_single_touch_fast_tap."""

    test_config = config.GestureConfig(
        slow_tap=config.SlowTapConfig(max_px=20, max_sec=20)
    )

    def test_process_one_new_active_tap_gesture(self) -> None:
        """One new active FAST TAP gesture."""
        processor = resolver.GestureResolver()
        gesture = utils.new_st_gesture(end=(-1, -1, -1, 1))

        processor._process_single_touch_fast_tap(gesture)

        assert 1 in processor._active_single_touches
        active = processor._active_single_touches[1]
        assert active["gesture"] is gesture
        assert active["tap_count"] == 1

    def test_process_two_new_active_tap_gestures(self) -> None:
        """Two new active FAST TAP gestures."""
        processor = resolver.GestureResolver()
        gesture1 = utils.new_st_gesture(end=(-1, -1, -1, 1))
        gesture2 = utils.new_st_gesture(end=(-1, -1, -1, 2))

        processor._process_single_touch_fast_tap(gesture1)
        processor._process_single_touch_fast_tap(gesture2)

        assert 1 in processor._active_single_touches
        active1 = processor._active_single_touches[1]
        assert active1["gesture"] is gesture1
        assert active1["tap_count"] == 1

        assert 2 in processor._active_single_touches
        active2 = processor._active_single_touches[2]
        assert active2["gesture"] is gesture2
        assert active2["tap_count"] == 1

    def test_process_increment_tap_count_on_threshold_met_once(self) -> None:
        """Subsequent FAST TAP increases tap count once."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_st_gesture(end=(100, 100, 10, 1))
        gesture2 = utils.new_st_gesture(end=(100, 119, 29, 1))
        processor._active_single_touches[1] = {
            "gesture": gesture1,
            "tap_count": 1,
        }

        processor._process_single_touch_fast_tap(gesture2)

        assert 1 in processor._active_single_touches
        active = processor._active_single_touches[1]
        assert active["gesture"] is gesture2
        assert active["tap_count"] == 2

    def test_process_increment_tap_count_on_threshold_met_twice(self) -> None:
        """Subsequent FAST TAPs increase tap count twice."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_st_gesture(end=(100, 100, 10, 1))
        gesture2 = utils.new_st_gesture(end=(100, 119, 29, 1))
        gesture3 = utils.new_st_gesture(end=(100, 138, 48, 1))
        processor._active_single_touches[1] = {
            "gesture": gesture1,
            "tap_count": 1,
        }

        processor._process_single_touch_fast_tap(gesture2)
        processor._process_single_touch_fast_tap(gesture3)

        assert 1 in processor._active_single_touches
        active = processor._active_single_touches[1]
        assert active["gesture"] is gesture3
        assert active["tap_count"] == 3

    def test_process_increment_tap_count_on_threshold_met_different_id(
        self,
    ) -> None:
        """Subsequent FAST TAPs increase tap count on different id gestures."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_st_gesture(end=(100, 100, 10, 1))
        gesture2 = utils.new_st_gesture(end=(100, 119, 29, 2))
        gesture3 = utils.new_st_gesture(end=(100, 119, 29, 1))
        processor._active_single_touches[1] = {
            "gesture": gesture1,
            "tap_count": 1,
        }
        processor._active_single_touches[2] = {
            "gesture": gesture2,
            "tap_count": 1,
        }

        processor._process_single_touch_fast_tap(gesture3)

        assert 1 in processor._active_single_touches
        active1 = processor._active_single_touches[1]
        assert active1["gesture"] is gesture3
        assert active1["tap_count"] == 2

        assert 2 in processor._active_single_touches
        active2 = processor._active_single_touches[2]
        assert active2["gesture"] is gesture2
        assert active2["tap_count"] == 1

    @pytest.mark.parametrize(
        ("y", "timestamp"),
        [
            (120, 29),  # Distance threshold is not met
            (119, 30),  # Duration threshold is not met
            (120, 30),  # Both are not met
        ],
    )
    def test_process_reset_tap_count_on_no_threshold_met(
        self, y: int, timestamp: int
    ) -> None:
        """Tap count is reset when threshold is not met."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_st_gesture(end=(100, 100, 10, 1))
        gesture2 = utils.new_st_gesture(end=(100, y, timestamp, 1))
        processor._active_single_touches[1] = {
            "gesture": gesture1,
            "tap_count": 3,
        }

        processor._process_single_touch_fast_tap(gesture2)

        assert 1 in processor._active_single_touches
        active = processor._active_single_touches[1]
        assert active["gesture"] is gesture2
        assert active["tap_count"] == 1


class TestGestureResolverProcessMultiTouchFastTap:
    """GestureResolver _process_multi_touch_fast_tap."""

    test_config = config.GestureConfig(
        slow_tap=config.SlowTapConfig(max_px=20, max_sec=20)
    )

    def test_process_new_active_tap_gesture(self) -> None:
        """New active FAST TAP gesture."""
        processor = resolver.GestureResolver()
        gesture = utils.new_mt_gesture()

        processor._process_multi_touch_fast_tap(gesture)

        assert processor._active_multi_touch["gesture"] is gesture
        assert processor._active_multi_touch["tap_count"] == 1

    def test_process_increment_tap_count_on_threshold_met_once(self) -> None:
        """Subsequent FAST TAP increases tap count once."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_mt_gesture(
            first_end=(100, 100, 10), second_end=(100, 100, 10)
        )
        gesture2 = utils.new_mt_gesture(
            first_end=(100, 119, 29), second_end=(100, 119, 29)
        )
        processor._active_multi_touch = {"gesture": gesture1, "tap_count": 1}

        processor._process_multi_touch_fast_tap(gesture2)

        assert processor._active_multi_touch["gesture"] is gesture2
        assert processor._active_multi_touch["tap_count"] == 2

    def test_process_increment_tap_count_on_threshold_met_twice(self) -> None:
        """Subsequent FAST TAPs increase tap count twice."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_mt_gesture(
            first_end=(100, 100, 10), second_end=(100, 100, 10)
        )
        gesture2 = utils.new_mt_gesture(
            first_end=(100, 119, 29), second_end=(100, 119, 29)
        )
        gesture3 = utils.new_mt_gesture(
            first_end=(100, 138, 48), second_end=(100, 138, 48)
        )
        processor._active_multi_touch = {"gesture": gesture1, "tap_count": 1}

        processor._process_multi_touch_fast_tap(gesture2)
        processor._process_multi_touch_fast_tap(gesture3)

        assert processor._active_multi_touch["gesture"] is gesture3
        assert processor._active_multi_touch["tap_count"] == 3

    @pytest.mark.parametrize(
        ("first_y", "first_timestamp", "second_y", "second_timestamp"),
        [
            (120, 29, 119, 29),  #  First: distance threshold is not met
            (119, 30, 119, 29),  #  First: duration threshold is not met
            (120, 30, 119, 29),  #  First: both are not met
            (120, 29, 120, 29),  # Second: distance threshold is not met
            (120, 29, 119, 30),  # Second: duration threshold is not met
            (120, 29, 120, 30),  # Second: both are not met
            (120, 30, 120, 30),  # First and second: both are not met
        ],
    )
    def test_process_reset_tap_count_on_no_threshold_met(
        self,
        first_y: int,
        first_timestamp: int,
        second_y: int,
        second_timestamp: int,
    ) -> None:
        """Tap count is reset when threshold is not met."""
        processor = resolver.GestureResolver(config=self.test_config)
        gesture1 = utils.new_mt_gesture(
            first_end=(100, 100, 10), second_end=(100, 100, 10)
        )
        gesture2 = utils.new_mt_gesture(
            first_end=(100, first_y, first_timestamp),
            second_end=(100, second_y, second_timestamp),
        )
        processor._active_multi_touch = {"gesture": gesture1, "tap_count": 3}

        processor._process_multi_touch_fast_tap(gesture2)

        assert processor._active_multi_touch["gesture"] is gesture2
        assert processor._active_multi_touch["tap_count"] == 1
