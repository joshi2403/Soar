# -*- coding: utf-8 -*-
"""Tests using pytest_resilient_circuits"""

from __future__ import print_function
import pytest
from resilient_circuits.util import get_config_data, get_function_definition
from resilient_circuits import SubmitTestFunction, FunctionResult

PACKAGE_NAME = "fn_pulsedive"
FUNCTION_NAME = "pulsedive_query_id"

# Read the default configuration-data section from the package
config_data = get_config_data(PACKAGE_NAME)

# Provide a simulation of the Resilient REST API (uncomment to connect to a real appliance)
resilient_mock = "pytest_resilient_circuits.BasicResilientMock"


def call_pulsedive_query_id_function(circuits, function_params, timeout=10):
    # Fire a message to the function
    evt = SubmitTestFunction("pulsedive_query_id", function_params)
    circuits.manager.fire(evt)
    event = circuits.watcher.wait("pulsedive_query_id_result", parent=evt, timeout=timeout)
    assert event
    assert isinstance(event.kwargs["result"], FunctionResult)
    pytest.wait_for(event, "complete", True)
    return event.kwargs["result"].value


class TestPulsediveQueryId:
    """ Tests for the pulsedive_query_id function"""

    def test_function_definition(self):
        """ Test that the package provides customization_data that defines the function """
        func = get_function_definition(PACKAGE_NAME, FUNCTION_NAME)
        assert func is not None

    @pytest.mark.livetest
    @pytest.mark.parametrize("pulsedive_id, pulsedive_id_type, pulsedive_id_report_type, expected_results", [
        (123, 'Indicator', 'Indicator Summary (using Threat ID only)', {"value": "xyz"}),
        (123, 'Indicator', 'General', {"value": "xyz"})
    ])
    def test_success(self, circuits_app, pulsedive_id, pulsedive_id_type, pulsedive_id_report_type, expected_results):
        """ Test calling with sample values for the parameters """
        function_params = { 
            "pulsedive_id": pulsedive_id,
            "pulsedive_id_type": pulsedive_id_type,
            "pulsedive_id_report_type": pulsedive_id_report_type
        }
        results = call_pulsedive_query_id_function(circuits_app, function_params)
        assert(expected_results == results)