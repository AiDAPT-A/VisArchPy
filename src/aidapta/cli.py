import typer
from typing import Optional

app = typer.Typer()

@app.command()
def hello(name: Optional[str] = None):

    if name:
        typer.echo(f"Hello {name}")
    else:
        typer.echo("Hello World")

if __name__ == "__main__":
    app()