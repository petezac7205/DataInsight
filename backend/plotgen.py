from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import matplotlib.pyplot as plt
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlotRequest(BaseModel):
    data: list
    chart_type: str
    x_column: str
    y_column: str | None = None

@app.post("/generate")
def generate_plot(request: PlotRequest):
    df = pd.DataFrame(request.data)

    plt.figure()

    if request.chart_type == "line":
        plt.plot(df[request.x_column], df[request.y_column])

    elif request.chart_type == "scatter":
        plt.scatter(df[request.x_column], df[request.y_column])

    elif request.chart_type == "bar":
        plt.bar(df[request.x_column], df[request.y_column])

    else:
        plt.plot([1,2,3], [4,5,6])

    plt.title(f"{request.chart_type.capitalize()} Plot")
    plt.xlabel(request.x_column)
    if request.y_column:
        plt.ylabel(request.y_column)

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    plt.close()

    return StreamingResponse(img_bytes, media_type="image/png")