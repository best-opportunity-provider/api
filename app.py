import uvicorn
import config
import endpoints  # noqa: F401

if __name__ == '__main__':
    uvicorn.run(config.app, host=config.HOST, port=config.PORT)
