from pathlib import Path

from streamlit.testing.v1 import AppTest


def app_path() -> Path:
    return Path(__file__).resolve().parents[1] / "app.py"


def open_workspace_section(app: AppTest, section: str) -> AppTest:
    workspace = next(item for item in app.segmented_control if item.label == "Learning workspace tabs")
    workspace.set_value(section)
    return app.run()


def test_overview_hero_and_calls_to_action_render() -> None:
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    assert not app.exception
    assert any("OpsReady Linux Lab" in item.value for item in app.markdown)
    assert any(button.label == "Start Learning" for button in app.button)
    assert any(button.label == "Run Health Simulation" for button in app.button)
    assert any(button.label == "Solve an Incident" for button in app.button)


def test_feedback_page_renders_without_exception() -> None:
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    navigation = next(item for item in app.radio if item.label == "Navigation")
    navigation.set_value("Feedback")
    app.run()

    assert not app.exception
    assert any(button.label == "Submit feedback" for button in app.button)
    # The page is valid in both deployment modes:
    # persistent webhook configured, or local preview fallback.


def test_successful_feedback_submission_clears_form(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPSREADY_FEEDBACK_FORCE_LOCAL", "true")
    monkeypatch.setenv("OPSREADY_FEEDBACK_FILE", str(tmp_path / "feedback.jsonl"))
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    navigation = next(item for item in app.radio if item.label == "Navigation")
    navigation.set_value("Feedback")
    app.run()

    next(item for item in app.selectbox if item.label == "Which option best describes you?").set_value(
        "Student or self-learner"
    )
    next(item for item in app.selectbox if item.label == "Your Linux experience").set_value("Beginner")
    next(item for item in app.multiselect if item.label == "What kind of feedback are you giving?").set_value(
        ["Usability"]
    )
    next(item for item in app.multiselect if item.label == "Which sections did you use?").set_value(
        ["Command Lab"]
    )
    next(item for item in app.text_area if item.label == "What should be improved first? *").set_value(
        "Clear the form after a successful submission."
    )
    next(item for item in app.checkbox if item.label.startswith("I agree that this feedback")).set_value(True)
    next(item for item in app.button if item.label == "Submit feedback").click()
    app.run()

    assert not app.exception
    assert next(item for item in app.selectbox if item.label == "Which option best describes you?").value is None
    assert next(item for item in app.selectbox if item.label == "Your Linux experience").value is None
    assert next(item for item in app.multiselect if item.label == "What kind of feedback are you giving?").value == []
    assert next(item for item in app.multiselect if item.label == "Which sections did you use?").value == []
    assert next(item for item in app.text_area if item.label == "What should be improved first? *").value == ""
    assert next(item for item in app.checkbox if item.label.startswith("I agree that this feedback")).value is False
    assert any("form has been cleared" in item.value for item in app.warning)


def test_health_simulator_changes_results_by_scenario() -> None:
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    app = open_workspace_section(app, "Health Dashboard")

    scenario = next(item for item in app.selectbox if item.label == "Choose a server scenario")
    scenario.set_value("CPU saturation")
    next(item for item in app.button if item.label == "Load scenario values").click()
    app.run()
    next(item for item in app.button if item.label == "Run simulated health check").click()
    app.run()
    assert any("Simulation result: Critical" in item.value for item in app.markdown)
    assert next(item for item in app.slider if item.label == "CPU usage (%)").value == 94
    assert any("Simulated server-health collection" in item.value for item in app.markdown)

    scenario = next(item for item in app.selectbox if item.label == "Choose a server scenario")
    scenario.set_value("Healthy baseline")
    next(item for item in app.button if item.label == "Load scenario values").click()
    app.run()
    next(item for item in app.button if item.label == "Run simulated health check").click()
    app.run()
    assert any("Simulation result: Normal" in item.value for item in app.markdown)
    assert next(item for item in app.slider if item.label == "CPU usage (%)").value == 32


def test_incident_lab_explains_its_learning_purpose() -> None:
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    app = open_workspace_section(app, "Incident Lab")
    assert not app.exception
    assert any("Purpose of the Incident Lab" in item.value for item in app.markdown)
    assert any("Simulated incident event log" in item.value for item in app.markdown)


def test_overview_cta_opens_command_lab() -> None:
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    next(item for item in app.button if item.label == "Start Learning").click()
    app.run()
    assert not app.exception
    assert any(item.label == "Command" for item in app.selectbox)


def open_assessment(app: AppTest) -> AppTest:
    navigation = next(item for item in app.radio if item.label == "Navigation")
    navigation.set_value("Assessment")
    return app.run()


def test_assessment_generates_only_after_explicit_button(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPSREADY_ASSESSMENT_CACHE_DIR", str(tmp_path / "tests"))
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    app = open_assessment(app)

    assert not app.exception
    assert any(button.label == "Generate test" for button in app.button)
    assert not any(item.label == "Submit all answers" for item in app.button)

    next(item for item in app.button if item.label == "Generate test").click()
    app.run()
    assert not app.exception
    question_headers = [item.value for item in app.markdown if "Question " in item.value and " of " in item.value]
    assert len(question_headers) == 10
    active_id = next(metric.value for metric in app.metric if metric.label == "Active test")

    app.run()
    assert next(metric.value for metric in app.metric if metric.label == "Active test") == active_id
    assert len([item for item in app.markdown if "Question " in item.value and " of " in item.value]) == 10



def test_assessment_uses_only_reviewed_random_bank(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPSREADY_ASSESSMENT_CACHE_DIR", str(tmp_path / "tests"))
    app = AppTest.from_file(str(app_path()), default_timeout=30).run()
    app = open_assessment(app)

    assert not app.exception
    assert not any(item.label == "Test generator" for item in app.radio)
    assert any("randomly without duplicates" in item.value for item in app.caption)
    assert not any("model generator" in item.value.lower() for item in app.markdown)
    next(item for item in app.button if item.label == "Generate test").click()
    app.run()
    assert next(metric.value for metric in app.metric if metric.label == "Source") == "Reviewed random bank"
