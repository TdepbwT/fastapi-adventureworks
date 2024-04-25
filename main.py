
from itertools import product
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from dbConn import conn
from datetime import datetime
    
app = FastAPI()
    
# Pydantic model to define the schema of the data for GET
class Products(BaseModel):
    ProductID: int 
    Name: str 
     
@app.get("/")
def root():
    return {"message": "Coursework - David A 26321509"}



# Route to return 50 products (MAX) from the production_product table via a GET request (no parameters used) without using a datamodel
# Adapted from Workshop 8 code - https://malkhafajiy.github.io/CMP2808M_23-24_labs/workshop8.html
# and also https://fastapi.tiangolo.com/tutorial/query-params/
@app.get("/products/allnomodel")
def get_all_products():
    cursor = conn.cursor()
    cursor.execute("SELECT ProductID, Name FROM Production_Product LIMIT 50")
    result = cursor.fetchall()
    return {"products": result}
    

# Route to return a specific product from the production_product table item via a GET request using a parameter (ProductID)
# Adapted from Workshop 8 code - https://malkhafajiy.github.io/CMP2808M_23-24_labs/workshop8.html
# and also https://fastapi.tiangolo.com/tutorial/query-params/
@app.get("/products/{product_id}", response_model=Products)
def read_item(product_id: int):
    cursor = conn.cursor()
    query = "SELECT ProductID, Name FROM Production_Product WHERE ProductID=%s"
    cursor.execute(query, (product_id,))
    item = cursor.fetchone()
    cursor.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ProductID": item[0], "Name": item[1]}

# model to define schema for POST request
class Product(BaseModel):
    Name: str
    ProductID: int
    ProductNumber: str
    rowguid: str
    SafetyStockLevel: int
    ReorderPoint: int
    StandardCost: float
    ListPrice: float
    DaysToManufacture: int
    SellStartDate: datetime
    
# POST endpoint to create a new product
@app.post("/products/", response_model=Products)
def create_product(product: Product):
    cursor = conn.cursor()
    query = """
    INSERT INTO Production_Product (ProductID, Name, ProductNumber, rowguid, SafetyStockLevel, ReorderPoint, StandardCost, ListPrice, DaysToManufacture, SellStartDate) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (product.ProductID, product.Name, product.ProductNumber, product.rowguid, product.SafetyStockLevel, product.ReorderPoint, product.StandardCost, product.ListPrice, product.DaysToManufacture, product.SellStartDate))
    conn.commit()
    new_product_id = cursor.lastrowid
    cursor.close()
    return {"ProductID": new_product_id, **product.dict()}

# model to define schema for customer POST request
class Customer(BaseModel):
    CustomerID: int
    PersonID: int
    StoreID: int
    TerritoryID: int
    AccountNumber: str
    rowguid: str
    ModifiedDate: datetime

# POST endpoint to create a new customer
@app.post("/customers/", response_model=Customer)
def create_customer(customer: Customer):
    cursor = conn.cursor()
    query = """
    INSERT INTO Sales_Customer (CustomerID, PersonID, StoreID, TerritoryID, AccountNumber, rowguid, ModifiedDate) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (customer.CustomerID, customer.PersonID, customer.StoreID, customer.TerritoryID, customer.AccountNumber, customer.rowguid, customer.ModifiedDate))
    conn.commit()
    new_customer_id = cursor.lastrowid
    cursor.close()
    return {"CustomerID": new_customer_id, **customer.dict()}

# PUT endpoint to update customer details
@app.put("/customers/{customer_id}", response_model=dict)
def update_customer(customer_id: int, customer: Customer):
    # check if customer exists
    cursor = conn.cursor()
    query = "SELECT CustomerID FROM Sales_Customer WHERE CustomerID = %s"
    cursor.execute(query, (customer_id,))
    existing_customer = cursor.fetchone()
    cursor.close()
    
    if existing_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # update customer info
    cursor = conn.cursor()
    query = """
    UPDATE Sales_Customer 
    SET PersonID=%s, StoreID=%s, TerritoryID=%s, AccountNumber=%s, rowguid=%s, ModifiedDate=%s
    WHERE CustomerID=%s
    """
    cursor.execute(query, (customer.PersonID, customer.StoreID, customer.TerritoryID, customer.AccountNumber, customer.rowguid, customer.ModifiedDate, customer_id))
    conn.commit()
    cursor.close()
    return {"message": "Customer updated successfully"}

#PUT endpoint to update product details
@app.put("/products/{product_id}", response_model=dict)
def update_product(product_id: int, product_update: Product):
    # check if product exists
    cursor = conn.cursor()
    query = "SELECT ProductID FROM Production_Product WHERE ProductID = %s"
    cursor.execute(query, (product_id,))
    existing_product = cursor.fetchone()
    cursor.close()

    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # update product info
    cursor = conn.cursor()
    query = """
    UPDATE Production_Product 
    SET Name = %s, ProductNumber = %s, SellStartDate = %s
    WHERE ProductID = %s
    """
    cursor.execute(query, (product_update.Name, product_update.ProductNumber, 
                           product_update.SellStartDate, product_id))
    conn.commit()
    cursor.close()
    
    return {"message": "Product information updated successfully"}

# DELETE endpoint to delete product
@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: int):
    # check if product exists
    cursor = conn.cursor()
    query = "SELECT ProductID FROM Production_Product WHERE ProductID = %s"
    cursor.execute(query, (product_id,))
    existing_product = cursor.fetchone()
    cursor.close()

    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # delete product
    cursor = conn.cursor()
    query = "DELETE FROM Production_Product WHERE ProductID = %s"
    cursor.execute(query, (product_id,))
    conn.commit()
    cursor.close()
    
    return {"message": "Product deleted successfully"}

#DELETE endpoint to delete customer
@app.delete("/customers/{customer_id}", response_model=dict)
def delete_customer(customer_id: int):
    # check if customer exists
    cursor = conn.cursor()
    query = "SELECT CustomerID FROM Sales_Customer WHERE CustomerID = %s"
    cursor.execute(query, (customer_id,))
    existing_customer = cursor.fetchone()
    cursor.close()

    if existing_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # delete customer
    cursor = conn.cursor()
    query = "DELETE FROM Sales_Customer WHERE CustomerID = %s"
    cursor.execute(query, (customer_id,))
    conn.commit()
    cursor.close()
    
    return {"message": "Customer deleted successfully"}