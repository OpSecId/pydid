"""Test Resource."""

from pydid.verification_method import (
    Ed25519VerificationKey2018,
    KnownVerificationMethods,
    VerificationMethod,
)
from typing import Optional
import pytest
from pydid.resource import Resource, IndexedResource


@pytest.fixture
def mock_indexed_resource():
    def _mock_indexed_resource(return_value=None):
        class MockIndexedResource(IndexedResource):
            def _index_resources(self):
                pass

            def dereference(self, reference: str) -> Resource:
                return return_value

        return MockIndexedResource()

    yield _mock_indexed_resource


def test_resource_json_transforms():
    class Test(Resource):
        one: str

    assert Test(one="test").to_json() == '{"one": "test"}'
    assert Test.from_json('{"one": "test"}') == Test(one="test")


def test_dereference_as_compatible(mock_indexed_resource):
    class One(Resource):
        common: str
        optiona: Optional[str] = None

    class Two(Resource):
        common: str

    test = mock_indexed_resource(One(common="common"))
    assert isinstance(test.dereference_as(One, "test"), One)
    assert isinstance(test.dereference_as(Two, "test"), Two)


def test_dereference_as_incompatible(mock_indexed_resource):
    class One(Resource):
        one: str

    class Two(Resource):
        two: str

    test = mock_indexed_resource(One(one="one"))
    assert isinstance(test.dereference_as(One, "test"), One)
    with pytest.raises(ValueError):
        test.dereference_as(Two, "test")


def test_dereference_as_vmethod(mock_indexed_resource):
    resource = Resource(
        id="did:example:123#key-1",
        controller="did:example:123",
        type="Ed25519VerificationKey2018",
        public_key_base58="testing",
    )
    test = mock_indexed_resource(resource)
    result = test.dereference_as(VerificationMethod, "test")
    assert isinstance(result, VerificationMethod)
    assert result.public_key_base58 == "testing"
    assert result.material == "testing"


def test_dereference_as_vmethod_x(mock_indexed_resource):
    resource = Resource(type="agent", service_endpoint="http://example.com")
    test = mock_indexed_resource(resource)
    with pytest.raises(ValueError):
        test.dereference_as(VerificationMethod, "test")


def test_dereference_as_vmethod_using_known_methods(mock_indexed_resource):
    resource = Resource(
        id="did:example:123#key-1",
        controller="did:example:123",
        type="Ed25519VerificationKey2018",
        public_key_base58="testing",
    )
    test = mock_indexed_resource(resource)
    result = test.dereference_as(KnownVerificationMethods, "test")
    assert isinstance(result, VerificationMethod)
    assert isinstance(result, Ed25519VerificationKey2018)
    assert result.public_key_base58 == "testing"
    assert result.material == "testing"


def test_dereference_as_vmethod_using_known_methods_x(mock_indexed_resource):
    resource = Resource(
        id="did:example:123#did-communication",
        service_endpoint="did:example:123",
        type="did-communication",
    )
    test = mock_indexed_resource(resource)
    with pytest.raises(ValueError):
        test.dereference_as(KnownVerificationMethods, "test")
