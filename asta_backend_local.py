import json
import traceback
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from timeit import default_timer as timer


async def get_data(document_name):
    with open(f'data/{document_name}', "r", encoding='utf-8') as f:
        data = json.load(f)
        return data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/get_meal/{mensa}")
async def get_meal_plan(mensa: int):
    result = "something went wrong please contact ASAP"
    start = timer()
    try:
        if mensa == 1:
            result = await get_data("mensa1")
        elif mensa == 2:
            result = await get_data("mensa2")
        elif mensa == 3:
            result = await get_data("mensa3")

    except Exception:
        traceback.print_exc()

    end = timer()
    print(f'[+] getting/sending mensa data for mensa nr. {mensa} took {end - start} seconds')
    return {"data": result}


if __name__ == "__main__":
    uvicorn.run(app,  host="127.0.0.1", port=8000)
