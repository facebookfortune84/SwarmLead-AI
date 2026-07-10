from core.workflows.outreach_sequences import OutreachSequences


def test_build_sequence():
    workflow = OutreachSequences()

    sequence = workflow.build_sequence(
        [
            "Message 1",
            "Message 2",
        ]
    )

    assert len(sequence) == 2
    assert sequence[0]["step"] == 1
    assert sequence[1]["step"] == 2


def test_first_touch():
    workflow = OutreachSequences()

    touch = workflow.first_touch(
        [
            "Hello",
            "Follow up",
        ]
    )

    assert touch["message"] == "Hello"


def test_first_touch_empty():
    workflow = OutreachSequences()

    assert workflow.first_touch([]) is None


def test_total_steps():
    workflow = OutreachSequences()

    assert (
        workflow.total_steps(
            [
                "one",
                "two",
                "three",
            ]
        )
        == 3
    )


def test_is_empty_true():
    workflow = OutreachSequences()

    assert workflow.is_empty([]) is True


def test_is_empty_false():
    workflow = OutreachSequences()

    assert workflow.is_empty(["hello"]) is False
