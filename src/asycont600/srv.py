import typer
from typing_extensions import Annotated
from typing import Union

from fastapi import FastAPI
import uvicorn

def greet(
  port: Annotated[int, typer.Option(help="Server TCP Port")] = 7300
): 
  app = FastAPI()

  @app.get("/")
  def read_root():
    return {"Hello": "World"}

  uvicorn.run(app, host="localhost", port=port, log_level="info")
    # greeting = "Greetings, dear "
    # masculine = gender == "masculine"
    # feminine = gender == "feminine"
    # if gender or knight:
    #     salutation = ""
    #     if knight:
    #         salutation = "Sir "
    #     elif masculine:
    #         salutation = "Mr. "
    #     elif feminine:
    #         salutation = "Ms. "
    #     greeting += salutation
    #     if name:
    #         greeting += f"{name}!"
    #     else:
    #         pronoun = "her" if feminine else "his" if masculine or knight else "its"
    #         greeting += f"what's-{pronoun}-name"
    # else:
    #     if name:
    #         greeting += f"{name}!"
    #     elif not gender:
    #         greeting += "friend!"
    # for i in range(0, count):
    #     print(greeting)

app = typer.Typer()
app.command()(greet)

if __name__ == "__main__":
    app()