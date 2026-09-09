import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.database import Base, get_db
from src.db.seed import seed_database
from src.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_client():
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
    assert data["total"] >= 5
    assert len(data["items"]) >= 5


@pytest.mark.asyncio
async def test_get_product_by_id(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products/prod_breville_barista_touch")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == "prod_breville_barista_touch"
    assert product["name"] == "Barista Touch Espresso Machine"
    assert product["height_cm"] == 40.7
    assert product["top_clearance_cm"] == 12.0


@pytest.mark.asyncio
async def test_get_nonexistent_product(test_client: AsyncClient):
    response = await test_client.get("/api/v1/products/non_existent_id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_by_dimensions(test_client: AsyncClient):
    # Search for items that fit in under 40 cm height
    response = await test_client.get("/api/v1/products/search/by-dimensions?max_height_cm=40")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    # Every item must have height_cm + top_clearance_cm <= 40
    for item in items:
        assert (item["height_cm"] + item["top_clearance_cm"]) <= 40.0

