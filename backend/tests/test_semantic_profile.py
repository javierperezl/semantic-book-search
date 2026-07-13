from app.semantic_profile import build_book_profile, build_query_profile, clean_subjects


def test_clean_subjects_dedup_and_filters_noise():
    subjects = [
        "Business",
        "business",  # duplicado case-insensitive
        "Accessible book",  # ruido
        "Leadership",
        "Protected DAISY",  # ruido
    ]
    result = clean_subjects(subjects)
    assert result == ["Business", "Leadership"]


def test_clean_subjects_respects_max():
    subjects = [f"Topic {i}" for i in range(20)]
    result = clean_subjects(subjects, max_subjects=5)
    assert len(result) == 5


def test_build_book_profile_includes_title_and_subjects():
    book = {
        "title": "Atomic Habits",
        "author": "James Clear",
        "year": 2018,
        "subjects": ["Self-help", "Accessible book"],
    }
    profile = build_book_profile(book)
    assert "Atomic Habits" in profile
    assert "James Clear" in profile
    assert "Self-help" in profile
    assert "Accessible book" not in profile


def test_build_query_profile_anchors_on_reference_book():
    reference = {
        "title": "Atomic Habits",
        "author": "James Clear",
        "subjects": ["Self-help", "Habit formation"],
    }
    profile = build_query_profile(reference, "Wants a business-focused version")
    assert "Atomic Habits" in profile
    assert "Wants a business-focused version" in profile


def test_build_query_profile_without_reference_falls_back():
    profile = build_query_profile(None, "Just the semantic description")
    assert profile == "Just the semantic description"
