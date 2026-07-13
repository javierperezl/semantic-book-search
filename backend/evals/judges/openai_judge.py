class OpenAIJudge:

    def evaluate(
        self,
        query: str,
        answer: str,
        books: list,
    ) -> float:

        raise NotImplementedError