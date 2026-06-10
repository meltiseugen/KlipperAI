from __future__ import annotations

import pytest

from klipperai_agent.llm import ConfigPromptPayload, StubConfigAssistantProvider
from klipperai_agent.printerconfig import ConfigRequestTarget, ConfigSnapshot
from klipperai_agent.printerprofile import PrinterProfile


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("feature", "expected_target"),
    [
        ("fan", "klipperai/fan.cfg"),
        ("macro", "klipperai/macros.cfg"),
        ("sensor", "klipperai/sensor.cfg"),
        ("probe", "klipperai/probe.cfg"),
        ("heater", "klipperai/heater.cfg"),
        ("input_shaper", "klipperai/input_shaper.cfg"),
        ("bed_mesh", "klipperai/bed_mesh.cfg"),
        ("filament", "klipperai/filament.cfg"),
        ("canbus", "klipperai/canbus.cfg"),
        ("stepper", "klipperai/stepper.cfg"),
        ("extruder", "klipperai/extruder.cfg"),
        ("generic", "klipperai/custom.cfg"),
    ],
)
async def test_stub_config_provider_returns_a_proposal_for_each_feature(
    feature: str,
    expected_target: str,
) -> None:
    provider = StubConfigAssistantProvider()
    payload = ConfigPromptPayload(
        user_message=f"Generate me a {feature} config",
        snapshot=ConfigSnapshot(root_file=None, documents=[], notes=[]),
        target=ConfigRequestTarget(feature=feature, rationale="test"),
        profile=PrinterProfile(),
    )

    result = await provider.propose(payload)

    assert result.proposals
    assert result.proposals[0].target_file == expected_target
