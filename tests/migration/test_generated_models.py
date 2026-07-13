import importlib
import pathlib


def test_all_generated_models_import():
    models = [
        "core.models.user",
        "core.models.api_key",
        "core.models.lead",
        "core.models.usage",
        "core.models.deployment",
        "core.models.tenant",
        "core.models.notification",
        "core.models.message",
        "core.models.message_thread",
        "core.models.workflow",
        "core.models.workflow_step",
        "core.models.ticket",
        "core.models.ticket_history",
        "core.models.ticket_comment",
    ]

    for module in models:
        importlib.import_module(module)
