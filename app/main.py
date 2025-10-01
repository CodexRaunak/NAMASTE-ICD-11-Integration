# download `pip install "fastapi[standardd]"`
from fastapi import FastAPI 

app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "Hello World"}

@app.get("/CodeSystem/{namaste}")
async def code_system(namaste: str):
    if namaste not in ["namaste_siddha_morbidity", "namaste_unani_morbidity", "namaste_ayurveda_morbidity", "ayurveda_standard_terminology"]:
        return {"message": "Not Found"}
    elif namaste == "namaste_siddha_morbidity":
        return {"message": f"{namaste}"}
    elif namaste == "namaste_unani_morbidity":
        return {"message": f"{namaste}"}
    elif namaste == "namaste_ayurveda_morbidity":
        return {"message": f"{namaste}"}
    elif namaste == "ayurveda_standard_terminology":
        return {"message": f"{namaste}"}

@app.get("/ValueSet/$expand?filter={filter}")
async def value_set_expand(filter: str):
    return {"message": f"ValueSet expand with filter: {filter}"}

# Run using `fastapi dev main.py`