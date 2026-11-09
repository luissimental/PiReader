from typing import TYPE_CHECKING

import pytest

from pireader.common import mixins

if TYPE_CHECKING:
    import pytest_mock


class TestInitReprMixinReprFields:
    """Test InitReprMixin _repr_fields."""

    def test_repr_fields_all_fields(self) -> None:
        """All fields are included."""

        class User(mixins.InitReprMixin):
            def __init__(self, name: str, age: int = 30) -> None:
                self.name = name
                self.age = age
                self._internal_state = "hidden"

        result = repr(User("Andy"))

        assert result == "User(name='Andy', age=30)"

    def test_repr_fields_include_some_fields(self) -> None:
        """Included fields are specified."""

        class Account(mixins.InitReprMixin):
            _repr_fields = ("email", "role")

            def __init__(
                self, email: str, password: str, role: str = "admin"
            ) -> None:
                self.email = email
                self.password = password
                self.role = role

        result = repr(Account("email@example.com", "passw0rd"))

        assert result == "Account(email='email@example.com', role='admin')"

    def test_repr_fields_included_in_private_attribute(self) -> None:
        """Included field is in a private attribute."""

        class Account(mixins.InitReprMixin):
            _repr_fields = ("email", "role")

            def __init__(
                self, email: str, password: str, role: str = "admin"
            ) -> None:
                self._email = email
                self._password = password
                self._role = role

        result = repr(Account("email@example.com", "passw0rd"))

        assert result == "Account(email='email@example.com', role='admin')"

    def test_repr_fields_included_not_present_safely_omitted(self) -> None:
        """Included field is not present but safely omitted."""

        class PartialInit(mixins.InitReprMixin):
            _repr_fields = ("a", "b", "non_existent_field")

            def __init__(self, a: int, b: int = 10) -> None:  # noqa: ARG002
                self.a = a

        result = repr(PartialInit(10, 20))

        assert result == "PartialInit(a=10)"

    def test_repr_fields_include_kwargs(self) -> None:
        """Kwarg fields are included."""

        class DynamicService(mixins.InitReprMixin):
            _repr_fields = ("name", "timeout")

            def __init__(self, name: str, **kwargs: object) -> None:
                self.name = name
                for k, v in kwargs.items():
                    setattr(self, k, v)

        result = repr(DynamicService("Auth", timeout=10, ignored_kwarg=True))

        assert result == "DynamicService(name='Auth', timeout=10)"

    def test_repr_fields_ignore_kwargs(self) -> None:
        """Ignore kwargs when fields is __all__."""

        class DynamicService(mixins.InitReprMixin):
            def __init__(self, name: str, **kwargs: object) -> None:
                self.name = name
                for k, v in kwargs.items():
                    setattr(self, k, v)

        result = repr(DynamicService("Auth", timeout=10, ignored_keyword=True))

        assert result == "DynamicService(name='Auth')"


class TestInitReprMixinReprExclude:
    """InitReprMixin _repr_exclude."""

    def test_repr_exclude_some_fields(self) -> None:
        """Excluded fields are ignored."""

        class Config(mixins.InitReprMixin):
            _repr_exclude = ("api_key", "secret")

            def __init__(self, host: str, api_key: str, secret: str) -> None:
                self.host = host
                self.api_key = api_key
                self.secret = secret

        result = repr(Config("localhost", "abc", "123"))

        assert result == "Config(host='localhost')"

    def test_repr_exclude_overrides_include(self) -> None:
        """Excluded fields override included fields."""

        class Conflict(mixins.InitReprMixin):
            _repr_fields = ("a", "b")
            _repr_exclude = ("b",)

            def __init__(self, a: int, b: int) -> None:
                self.a = a
                self.b = b

        result = repr(Conflict(1, 2))

        assert result == "Conflict(a=1)"


class TestInitReprMixinReprParamMap:
    """InitReprMixin _repr_param_map."""

    def test_repr_param_map_success(self) -> None:
        """Included field has a different attribute name."""

        class User(mixins.InitReprMixin):
            _repr_fields = ("name", "age")
            _repr_param_map = frozendict(name="user_name")

            def __init__(self, name: str, age: int) -> None:
                self.user_name = name
                self.age = age

        result = repr(User("Amy", 25))

        assert result == "User(name='Amy', age=25)"

    def test_repr_param_map_attribute_name_not_present(self) -> None:
        """Attribute name does not exist."""

        class User(mixins.InitReprMixin):
            _repr_fields = ("name", "age")
            _repr_param_map = frozendict(age="user_age")

            def __init__(self, name: str, age: int) -> None:
                self.name = name
                self.age = age

        result = repr(User("John", 20))

        assert result == "User(name='John')"


class TestInitReprMixinReprDirtyOnly:
    """InitReprMixin _repr_dirty_only."""

    def test_repr_dirty_only_mode(self) -> None:
        """Dirty mode only includes non-default."""

        class Settings(mixins.InitReprMixin):
            _repr_dirty_only = True

            def __init__(
                self, env: str, retries: int = 3, *, debug: bool = False
            ) -> None:
                self.env = env
                self.retries = retries
                self.debug = debug

        result1 = repr(Settings("prod"))
        result2 = repr(Settings("dev", debug=True))

        assert result1 == "Settings(env='prod')"
        assert result2 == "Settings(env='dev', debug=True)"


@pytest.mark.parametrize("error_type", [ValueError, TypeError])
def test_signature_inspection_failure_fallback(
    mocker: pytest_mock.MockerFixture, error_type: ValueError | TypeError
) -> None:
    """Gracefully fall back to empty params."""

    class Unavailable(mixins.InitReprMixin):
        def __init__(self, x: int) -> None:
            self.x = x

    mocker.patch("inspect.signature", side_effect=error_type)

    result = repr(Unavailable(42))
    assert result == "Unavailable()"
