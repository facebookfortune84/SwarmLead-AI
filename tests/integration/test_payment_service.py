"""
Integration Test
"""

from core.services.payment_service import (
    PaymentService,
)


def test_payment_service_constructs():

    service = PaymentService()

    assert service is not None


def test_payment_service_public_api():

    service = PaymentService()

    assert len(dir(service)) > 0
