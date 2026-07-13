import httpx
import pytest
import respx

from app.openlibrary import OpenLibraryError, multi_search, search_books


@pytest.mark.asyncio
@respx.mock
async def test_search_books_parses_docs():
    respx.get("https://openlibrary.org/search.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "docs": [
                    {
                        "title": "Atomic Habits",
                        "author_name": ["James Clear"],
                        "first_publish_year": 2018,
                        "subject": ["Self-help"],
                        "key": "/works/OL123W",
                    }
                ]
            },
        )
    )

    async with httpx.AsyncClient() as client:
        books = await search_books(client, "atomic habits", limit=1)

    assert len(books) == 1
    assert books[0]["title"] == "Atomic Habits"
    assert books[0]["author"] == "James Clear"


@pytest.mark.asyncio
@respx.mock
async def test_search_books_raises_on_http_error():
    respx.get("https://openlibrary.org/search.json").mock(
        return_value=httpx.Response(500)
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(OpenLibraryError):
            await search_books(client, "anything", limit=1)


@pytest.mark.asyncio
@respx.mock
async def test_multi_search_dedupes_and_survives_one_failing_query():
    respx.get("https://openlibrary.org/search.json", params={"q": "ok query"}).mock(
        return_value=httpx.Response(
            200,
            json={"docs": [{"title": "Book A", "key": "/works/OL1W"}]},
        )
    )
    respx.get("https://openlibrary.org/search.json", params={"q": "bad query"}).mock(
        return_value=httpx.Response(500)
    )

    results = await multi_search(["ok query", "bad query"], limit_per_query=5)

    assert len(results) == 1
    assert results[0]["title"] == "Book A"
