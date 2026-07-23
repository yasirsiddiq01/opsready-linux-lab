from collections import Counter

from opsready_lab.catalog.commands import COMMANDS
from opsready_lab.services.guided_output import guided_output_for, overridden_commands


def test_placeholder_outputs_are_all_replaced() -> None:
    for command, item in COMMANDS.items():
        rendered = guided_output_for(command, str(item["example"]), item["output"])
        assert "simulated matching record" not in rendered
        assert "another record selected by the command" not in rendered


def test_common_guided_commands_have_command_correct_outputs() -> None:
    checks = {
        "whoami": "appuser",
        "uname": "Linux opsready-lab",
        "head": "root:x:0:0",
        "awk": "student /bin/bash",
        "wc": "127 /var/log/syslog",
        "uniq": "502",
        "less": "/var/log/syslog (END)",
    }
    for command, expected in checks.items():
        item = COMMANDS[command]
        rendered = guided_output_for(command, str(item["example"]), item["output"])
        assert expected in rendered


def test_repeated_catalog_groups_receive_specific_overrides() -> None:
    counts = Counter(str(item["output"]) for item in COMMANDS.values())
    repeated_commands = {command for command, item in COMMANDS.items() if counts[str(item["output"])] > 1}
    missing = repeated_commands - overridden_commands()
    assert not missing, f"Repeated catalogue outputs need overrides: {sorted(missing)}"


def test_guided_outputs_are_not_one_repeated_template() -> None:
    outputs = [guided_output_for(command, str(item["example"]), item["output"]) for command, item in COMMANDS.items()]
    assert len(set(outputs)) >= 145
