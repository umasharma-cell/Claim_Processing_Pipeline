"""Unit tests for bill total calculation logic."""

import pytest
from app.agents.bill_agent import calculate_total, _safe_float


class TestSafeFloat:
    def test_integer(self):
        assert _safe_float(100) == 100.0

    def test_float(self):
        assert _safe_float(99.99) == 99.99

    def test_string(self):
        assert _safe_float("150.50") == 150.50

    def test_string_with_commas(self):
        assert _safe_float("1,500.00") == 1500.00

    def test_none(self):
        assert _safe_float(None) is None

    def test_invalid_string(self):
        assert _safe_float("not-a-number") is None

    def test_empty_string(self):
        assert _safe_float("") is None


class TestCalculateTotal:
    def test_basic_sum(self):
        items = [
            {"amount": 100.0},
            {"amount": 200.0},
            {"amount": 50.0},
        ]
        assert calculate_total(items) == 350.0

    def test_with_none_amounts(self):
        items = [
            {"amount": 100.0},
            {"amount": None},
            {"amount": 200.0},
        ]
        assert calculate_total(items) == 300.0

    def test_empty_items(self):
        assert calculate_total([]) is None

    def test_all_none_amounts(self):
        items = [
            {"amount": None},
            {"amount": None},
        ]
        assert calculate_total(items) is None

    def test_single_item(self):
        items = [{"amount": 42.50}]
        assert calculate_total(items) == 42.50

    def test_rounding(self):
        items = [
            {"amount": 10.1},
            {"amount": 20.2},
            {"amount": 30.3},
        ]
        result = calculate_total(items)
        assert result == 60.6

    def test_string_amounts(self):
        items = [
            {"amount": "100.00"},
            {"amount": "250.50"},
        ]
        assert calculate_total(items) == 350.50

    def test_missing_amount_key(self):
        items = [
            {"description": "Something"},
        ]
        assert calculate_total(items) is None
