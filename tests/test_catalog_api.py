import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.db.database import Base, get_db
from src.db.seed import seed_database
from src.main import app

TEST_DB_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("SQL_DB") or settings.DATABASE_URL


@pytest.fixture
async def test_client():
    if not TEST_DB_URL:
        pytest.skip("No database URL configured for test execution.")

    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    test_session_local = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_local() as session:
        await seed_database(session)

    async def override_get_db():
        async with test_session_local() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "product-catalog-service"


@pytest.mark.asyncio
async def test_list_products(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 10
    assert len(data["items"]) >= 10


@pytest.mark.asyncio
async def test_get_product_by_slug_or_id(test_client: AsyncClient):
    # Test lookup by slug
    response = await test_client.get("/api/v1/products/attikan-estate")
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Attikan Estate"
    assert product["brand"] == "Hiljhil Roasters"
    assert product["roast_level"] == "medium_dark"
    assert "Dark Chocolate" in product["taste_notes"]
    assert len(product["variants"]) >= 3


@pytest.mark.asyncio
async def test_filter_by_roast_level(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products?roast_level=light")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["roast_level"] == "light"


@pytest.mark.asyncio
async def test_filter_by_estate_name(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products?estate_name=Riverdale")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "Riverdale" in data["items"][0]["name"]


@pytest.mark.asyncio
async def test_get_nonexistent_product(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products/non_existent_id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_by_dimensions(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products/search/by-dimensions?max_height_cm=25")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    for item in items:
        assert (item["height_cm"] + item["top_clearance_cm"]) <= 25.0


@pytest.mark.asyncio
async def test_create_product_auto_sku(test_client: AsyncClient):
    payload = {
        "name": "Ratnagiri Estate Honey Anaerobic",
        "category": "producer_series",
        "price": 680.0,
        "estate_name": "Ratnagiri Estate",
        "weight_kg": 0.25,
        "variants": [
            {"size": "250g", "price": 680.0},
            {"size": "500g", "price": 1280.0},
        ],
    }
    response = await test_client.post("/api/v1/products", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["sku"] == "HJ-RATNAGIRI-250"
    assert created["slug"] == "ratnagiri-estate-honey-anaerobic"
    assert len(created["variants"]) == 2
    assert created["variants"][0]["sku"] == "HJ-RATNAGIRI-250G"
    assert created["variants"][1]["sku"] == "HJ-RATNAGIRI-500G"


@pytest.mark.asyncio
async def test_get_catalog_facets(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products/facets")
    assert response.status_code == 200
    facets = response.json()
    assert len(facets["categories"]) > 0
    assert "Hiljhil Roasters" in facets["brands"]
    assert len(facets["roast_levels"]) > 0
    assert len(facets["estates"]) > 0
    assert facets["min_price"] > 0
    assert facets["total_products"] >= 10


@pytest.mark.asyncio
async def test_get_product_by_sku(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products/sku/HJ-ATTIKAN-250")
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Attikan Estate"
    assert product["sku"] == "HJ-ATTIKAN-250"


@pytest.mark.asyncio
async def test_publish_and_archive_lifecycle(test_client: AsyncClient):
    # Archive Attikan
    archive_res = await test_client.post("/api/v1/products/attikan-estate/archive")
    assert archive_res.status_code == 200
    assert archive_res.json()["status"] == "archived"

    # Publish Attikan
    publish_res = await test_client.post("/api/v1/products/attikan-estate/publish")
    assert publish_res.status_code == 200
    assert publish_res.json()["status"] == "active"


@pytest.mark.asyncio
async def test_bulk_upsert_products(test_client: AsyncClient):
    payload = {
        "products": [
            {
                "name": "Coorg Robusta Special",
                "category": "single_estate",
                "price": 450.0,
                "weight_kg": 0.25,
            },
            {
                "name": "Mysore Nugget Extra Bold",
                "category": "blends",
                "price": 550.0,
                "weight_kg": 0.5,
            },
        ]
    }
    response = await test_client.post("/api/v1/products/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["inserted"] + data["updated"] == 2
