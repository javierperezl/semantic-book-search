PROMPT_TEMPLATE = """
You are helping build a semantic book search engine.

Given a user's request, return JSON with exactly these keys:

- intent (string)
- reference_books (array of strings, can be empty)
- search_queries (array of 3-5 short strings that maximize retrieval from Open Library)
- semantic_description (string): describes the KIND of book the user wants,
  not the exact search query.

Example:

User:
I want a book like Atomic Habits but for business

Output:
{{
    "intent": "find_similar_books",
    "reference_books": ["Atomic Habits"],
    "search_queries": [
        "business habits",
        "organizational behavior",
        "leadership",
        "business productivity"
    ],
    "semantic_description": "The user is looking for a practical non-fiction business book with the same actionable, habit-based and self-improvement style as Atomic Habits, but focused on business, leadership and organizational performance."
}}

User:

{query}
"""