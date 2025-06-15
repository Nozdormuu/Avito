import pytest
import requests
import random
import json

# Конфигурация
BASE_URL = "https://qa-internship.avito.com"

# Фикстуры
@pytest.fixture(scope="session")
def seller_id():
    return random.randint(111111, 999999)

@pytest.fixture
def advertisement_data(seller_id):
    return {
        "sellerID": seller_id,
        "name": "Тестовый товар",
        "price": 1000,
        "statistics": {
            "likes": 10,
            "viewCount": 20,
            "contacts": 5
        }
    }

@pytest.fixture
def created_advertisement(advertisement_data):
    response = requests.post(
        f"{BASE_URL}/api/1/item",
        json=advertisement_data,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    return response.json()

# Тесты создания объявлений
class TestCreateAdvertisement:
    def test_create_valid(self, seller_id):
        data = {
            "sellerID": seller_id,
            "name": "Новый товар",
            "price": 5000,
            "statistics": {"likes": 15, "viewCount": 30, "contacts": 10}
        }
        response = requests.post(f"{BASE_URL}/api/1/item", json=data)
        assert response.status_code == 200
        result = response.json()
        assert "id" in result
        assert result["sellerId"] == seller_id
        assert result["name"] == "Новый товар"
        assert result["price"] == 5000
        assert result["statistics"]["likes"] == 15

    @pytest.mark.parametrize("payload,expected_code", [
        ({"name": "Товар без sellerID", "price": 100}, 400),
        ({"sellerID": 123456, "price": 100}, 400),
        ({"sellerID": 123456, "name": "Товар без цены"}, 400),
        ({"sellerID": "не число", "name": "Товар", "price": 100}, 400),
        ({"sellerID": 100000, "name": "Товар", "price": 100}, 400),
        ({"sellerID": 1000000, "name": "Товар", "price": 100}, 400),
        ({"sellerID": 123456, "name": "Товар", "price": -100}, 400),
    ])
    def test_create_invalid(self, payload, expected_code):
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
        assert response.status_code == expected_code

# Тесты чтения данных
class TestReadOperations:
    def test_get_by_id(self, created_advertisement):
        ad_id = created_advertisement["id"]
        response = requests.get(f"{BASE_URL}/api/1/item/{ad_id}")
        assert response.status_code == 200
        ad_data = response.json()[0]
        assert ad_data["id"] == ad_id
        assert ad_data["name"] == created_advertisement["name"]

    def test_get_nonexistent(self):
        response = requests.get(f"{BASE_URL}/api/1/item/nonexistent_id")
        assert response.status_code == 404

    def test_get_by_seller(self, seller_id, created_advertisement):
        # Создаем второе объявление для того же продавца
        ad2_data = {
            "sellerID": seller_id,
            "name": "Второй товар",
            "price": 2000,
            "statistics": {"likes": 5, "viewCount": 10, "contacts": 2}
        }
        ad2 = requests.post(f"{BASE_URL}/api/1/item", json=ad2_data).json()
        
        response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
        assert response.status_code == 200
        ads = response.json()
        assert len(ads) >= 2
        ad_ids = {ad["id"] for ad in ads}
        assert created_advertisement["id"] in ad_ids
        assert ad2["id"] in ad_ids

    def test_get_empty_seller(self, seller_id):
        # Используем несуществующего продавца
        response = requests.get(f"{BASE_URL}/api/1/{seller_id + 1}/item")
        assert response.status_code == 200
        assert len(response.json()) == 0

# Тесты статистики
class TestStatistics:
    @pytest.mark.parametrize("api_version", [1, 2])
    def test_get_statistics(self, created_advertisement, api_version):
        ad_id = created_advertisement["id"]
        response = requests.get(f"{BASE_URL}/api/{api_version}/statistic/{ad_id}")
        assert response.status_code == 200
        stats = response.json()
        assert isinstance(stats, list)
        assert len(stats) > 0
        assert stats[0]["likes"] == 10
        assert stats[0]["viewCount"] == 20

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_nonexistent_statistics(self, api_version):
        response = requests.get(f"{BASE_URL}/api/{api_version}/statistic/nonexistent_id")
        assert response.status_code == 404

# Тесты удаления
class TestDeleteOperations:
    def test_delete_and_verify(self, advertisement_data):
        # Создаем объявление для удаления
        create_resp = requests.post(f"{BASE_URL}/api/1/item", json=advertisement_data)
        ad = create_resp.json()
        
        # Удаляем объявление
        delete_resp = requests.delete(f"{BASE_URL}/api/2/item/{ad['id']}")
        assert delete_resp.status_code == 200
        
        # Проверяем, что объявление удалено
        get_resp = requests.get(f"{BASE_URL}/api/1/item/{ad['id']}")
        assert get_resp.status_code == 404

    def test_double_delete(self, created_advertisement):
        ad_id = created_advertisement["id"]
        first_delete = requests.delete(f"{BASE_URL}/api/2/item/{ad_id}")
        assert first_delete.status_code == 200
        
        second_delete = requests.delete(f"{BASE_URL}/api/2/item/{ad_id}")
        assert second_delete.status_code == 404

    def test_delete_nonexistent(self):
        response = requests.delete(f"{BASE_URL}/api/2/item/nonexistent_id")
        assert response.status_code == 404