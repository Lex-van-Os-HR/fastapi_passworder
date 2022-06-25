import traceback
import uvicorn
import yaml
import logging
import socket
from typing import Optional

from fastapi import FastAPI, HTTPException

from passworder import Passworder
from random_password import get_random_salt
from pydantic import BaseModel


class EncryptRequest(BaseModel):
    salt: Optional[str] = None
    cleartext: str
    algorithm: Optional[str] = Passworder.DEFAULT_ALGO
    random_salt: Optional[bool] = True


with open("settings.yaml") as settings_file:
    settings = yaml.safe_load(settings_file)
    docker_volume_config = settings['logging_directory'] + "\
        passworder_logger.log"

    # dynamic load log location
    # logger_path = settings['logging_directory']
    # path_exists = os.path.exists(logger_path)

    # if path_exists:
    #     logging.info("Directory exists")
    # elif not path_exists:
    #     os.makedirs(logger_path)
    #     logging.info('Logging directory set')
        
main_parameters = {}
if not settings["openapi_console"]:
    main_parameters["docs_url"] = None

app = FastAPI(**main_parameters)
passworder = Passworder()

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Creating logger
passworder_logger = logging.getLogger('passworder_logger')
passworder_logger.setLevel(logging.INFO)

# Creating logger handlers
passworder_file_handler = logging.FileHandler(docker_volume_config)
passworder_file_handler.setLevel(logging.INFO)

# Creating logger formatters
passworder_file_formatter = logging.Formatter(
    '%(levelname)s: %(asctime)s %(message)s')
passworder_file_handler.setFormatter(passworder_file_formatter)

# Adding handlers to logger
passworder_logger.addHandler(passworder_file_handler)


def log_request(status_code, encryption_method):
    print("Logging passworder request...")

    # Get IP adress
    hostname=socket.gethostname()   
    ipAdress=socket.gethostbyname(hostname)   

    message = str(status_code) + " " + str(ipAdress) + " " + encryption_method
    passworder_logger.info(message) 
    print("Done logging")


@app.get("/encrypt/generators")
async def generators_list():
    return [list(Passworder.ALGO_MAP.keys())]


@app.get("/encrypt/version")
async def show_version():
    try:
        with open("version.txt", "r") as version_file:
            version = version_file.read()
            version = version.strip()
        return {"version": version}
    except FileNotFoundError as e:
        print(e)
        raise HTTPException(status_code=503,
         detail="Version file missing or not readeable")


@app.post("/encrypt/")
async def encrypt(encrypt_request: EncryptRequest):
    result = {}
    try:
        # Request validation steps..
        if not encrypt_request.cleartext:
            log_request(400, encrypt_request.algorithm)
            raise HTTPException(status_code=400,
             detail="Missing cleartext entry to encrypt")
        if not encrypt_request.random_salt and not encrypt_request.salt:
            log_request(400, encrypt_request.algorithm)
            raise HTTPException(status_code=400,
             detail="Either random salt or a set salt should be given")

        parameters = encrypt_request.dict()

        # It could be a random salt was requested. In this case, generate one
        # and include it in the function call
        if parameters.get("random_salt"):
            parameters["salt"] = get_random_salt()
        del parameters["random_salt"]

        shadow_string = passworder.get_linux_password(**parameters)

        result = {
            "shadow_string": shadow_string,
            "salt": parameters["salt"],
        }

        log_request(200, encrypt_request.algorithm)

    except HTTPException as e:
        # Raising the HTTP exception here, otherwise it will be picked up by
        # the generic exception handler
        log_request(404, encrypt_request.algorithm)
        raise e
    except Exception as e:
        print(e)
        traceback.print_exc()
        log_request(503, encrypt_request.algorithm)
        raise HTTPException(status_code=503, detail=str(e))
    finally:
        return result


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=settings["reload"],
     host=settings["listen_address"],
                port=settings["listen_port"])
