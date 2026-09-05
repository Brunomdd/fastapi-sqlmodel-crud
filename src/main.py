from fastapi import FastAPI
app = FastAPI()
@app.get("/teste",tags=['teste'])
def buscar_():
    return {"ola":"teste"}