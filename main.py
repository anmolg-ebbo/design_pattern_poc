import os
import click
import uvicorn

# Ensure config is loaded after setting env variables
def load_config():
    global config
    from core.config import get_config
    config = get_config()

@click.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "prod"], case_sensitive=False),
    default="dev",
)
@click.option(
    "--debug",
    type=click.BOOL,
    is_flag=True,
    default=False,
)
def main(env: str, debug: bool):
    os.environ["ENV"] = env
    os.environ["DEBUG"] = str(debug)

    # Reload config after setting environment variables
    load_config()

    uvicorn.run(
        app="app.server:app",
        host=config.APP_HOST,  # No more AttributeError
        port=config.APP_PORT,
        reload=True if config.ENV != "production" else False,
        workers=1,
    )


if __name__ == "__main__":
    main()
