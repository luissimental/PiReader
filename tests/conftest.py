import sys
from unittest import mock

sys.modules["spidev"] = mock.MagicMock()
