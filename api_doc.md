# Merinozky Management App API Documentation

## Authentication
All API endpoints require authentication. Use Bearer token authentication by including the following header:
```
Authorization: Bearer <your-token>
```

## Base URL
```
/api/v1/
```

## Products API

### List Products
```http
GET /products/
```
Returns a list of all products.

### Get Single Product
```http
GET /products/{code}/
```
Returns details of a specific product.

### Create Product
```http
POST /products/
```
Create a new product.

### Update Product
```http
PUT /products/{code}/
```
Update an existing product.

### Delete Product
```http
DELETE /products/{code}/
```
Delete a product.

### Adjust Product Stock
```http
POST /products/{code}/adjust_stock/
```
Adjust stock level for a product.

Request body:
```json
{
    "adjustment_quantity": 10
}
```

## Product Variants API

### List Variants
```http
GET /variants/
```
Returns a list of all product variants.

### Get Single Variant
```http
GET /variants/{code}/
```
Returns details of a specific variant.

### Create Variant
```http
POST /variants/
```
Create a new product variant.

### Update Variant
```http
PUT /variants/{code}/
```
Update an existing variant.

### Delete Variant
```http
DELETE /variants/{code}/
```
Delete a variant.

### Adjust Variant Stock
```http
POST /variants/{code}/adjust_stock/
```
Adjust stock level for a variant.

Request body:
```json
{
    "adjustment_quantity": 10
}
```

## Stock Adjustment
```http
POST /stock-adjustments/
```

Request body for single product using code or id:
```json
{
    "product_code":"P00018",
    "adjustment_quantity": 99
}
```

```json
{
    "product":1,
    "adjustment_quantity": 99
}
```

Request body for single variant using code or id:
```json
{
    "variant_code":"P00018-5",
    "adjustment_quantity": 99
}
```

```json
{
    "variant":1,
    "adjustment_quantity": 5
}
```

bulk adjustment for given products and variants

Request body for single variant using code:
```json
[
{
    "variant_code":"P00018-5",
    "adjustment_quantity": 5
},
{
    "product_code":"P00018",
    "adjustment_quantity": -18
},
{
    "variant":1,
    "adjustment_quantity": 5
},
{
    "product":1,
    "adjustment_quantity": 99
}
]
```


## Orders API

### List Orders
```http
GET /orders/
```
Returns a list of all orders.

### Get Single Order
```http
GET /orders/{id}/
```
Returns details of a specific order including its items.

### Update Order
```http
PUT /orders/{id}/
```
Update an existing order.

## Response Formats

### Success Response
```json
{
    "data": {},
    "message": "Operation successful"
}
```

### Error Response
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error message description"
    }
}
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
