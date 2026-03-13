import json
import os
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/products", tags=["products"])

PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "products.json")


def load_products():
    try:
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        save_products([])
        return []
    except json.JSONDecodeError:
        save_products([])
        return []


def save_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(products, file, ensure_ascii=False, indent=4)


@router.get("/")
async def get_products(
        sort_by: str = Query(None, description="Поле для сортировки (name, sport_type, price)"),
        sort_order: str = Query("asc", description="Порядок сортировки (asc, desc)")
):
    products = load_products()
    products_list = products.copy()

    if sort_by:
        if sort_by not in ["name", "sport_type", "price"]:
            raise HTTPException(
                status_code=400,
                detail="sort_by должен быть 'name', 'sport_type' или 'price'"
            )

        reverse = sort_order.lower() == "desc"

        if sort_by == "price":
            products_list.sort(key=lambda x: x["price"], reverse=reverse)
        else:
            products_list.sort(key=lambda x: x[sort_by].lower(), reverse=reverse)

    return {
        "products": products_list,
        "total": len(products_list),
        "sorting": f"by {sort_by} {sort_order}" if sort_by else "not applied"
    }


@router.get("/sport/{sport_type}")
async def get_products_by_sport(
        sport_type: str,
        sort_by: str = Query(None, description="Поле для сортировки (name, sport_type, price)"),
        sort_order: str = Query("asc", description="Порядок сортировки (asc, desc)")
):
    products = load_products()

    filtered_products = [
        product for product in products
        if product["sport_type"].lower() == sport_type.lower()
    ]

    if not filtered_products:
        raise HTTPException(
            status_code=404,
            detail=f"Товары для вида спорта '{sport_type}' не найдены"
        )

    products_list = filtered_products.copy()

    if sort_by:
        if sort_by not in ["name", "sport_type", "price"]:
            raise HTTPException(
                status_code=400,
                detail="sort_by должен быть 'name', 'sport_type' или 'price'"
            )

        reverse = sort_order.lower() == "desc"

        if sort_by == "price":
            products_list.sort(key=lambda x: x["price"], reverse=reverse)
        else:
            products_list.sort(key=lambda x: x[sort_by].lower(), reverse=reverse)

    return {
        "sport_type": sport_type,
        "products": products_list,
        "total": len(products_list),
        "sorting": f"by {sort_by} {sort_order}" if sort_by else "not applied"
    }


@router.post("/")
async def create_product(
        name: str = Query(..., description="Название товара"),
        sport_type: str = Query(..., description="Вид спорта"),
        price: float = Query(..., description="Цена товара", gt=0)
):
    products = load_products()

    # Создаем словарь с товаром из параметров запроса
    product = {
        "name": name,
        "sport_type": sport_type,
        "price": price
    }

    # Проверка на дубликат
    for existing_product in products:
        if existing_product["name"].lower() == product["name"].lower():
            raise HTTPException(
                status_code=400,
                detail=f"Товар '{product['name']}' уже существует"
            )

    # Генерация ID
    if products:
        new_id = max(p["id"] for p in products) + 1
    else:
        new_id = 1

    # Создаем новый товар с ID
    new_product = {
        "id": new_id,
        "name": product["name"],
        "sport_type": product["sport_type"],
        "price": product["price"]
    }

    products.append(new_product)
    save_products(products)

    return {
        "message": f"Товар '{new_product['name']}' успешно добавлен с ID {new_id}",
        "product": new_product
    }