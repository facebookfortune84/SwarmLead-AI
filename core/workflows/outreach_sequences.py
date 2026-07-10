class OutreachSequences:
    """
    Generates structured outreach sequences
    from outreach messages.
    """

    def build_sequence(
        self,
        messages,
    ):
        sequence = []

        for i, message in enumerate(messages, start=1):
            sequence.append(
                {
                    "step": i,
                    "message": message,
                }
            )

        return sequence

    def first_touch(self, messages):
        sequence = self.build_sequence(messages)

        if not sequence:
            return None

        return sequence[0]

    def total_steps(self, messages):
        return len(messages)

    def is_empty(self, messages):
        return len(messages) == 0
