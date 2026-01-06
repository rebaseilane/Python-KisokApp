from db import engine

try:
    engine.connect()
    print("Connected successfully!!")
except Exception as e:
    print("Connection failed:", e)
