import sys
from datetime import datetime

import mlflow
from mlflow import MlflowClient, MlflowException
from mlflow.entities.model_registry import RegisteredModel

from src.config.settings import MODEL_NAME, MODEL_VERSION_ALIAS

client = MlflowClient()

def print_model_info(rm: RegisteredModel):
    print("--Model--")
    print("Name: {}".format(rm.name))
    print("Aliases: {}".format(rm.aliases))
    print("Last Updated Timestamp: {}".format(datetime.fromtimestamp(rm.last_updated_timestamp / 1000)))


def show():
    print("### SHOW ###")
    client = MlflowClient()
    for res in client.search_model_versions():
        print(f"name={res.name}; run_id={res.run_id}; version={res.version}")


def deploy():
    mlflow.set_experiment("rawiq-quickstart")

    data_example = {
        "messages": [{"role": "user", "content": "What is MLflow?"}],
        # "max_tokens": 25,
    }

    with mlflow.start_run() as run:
        model_info = mlflow.pyfunc.log_model(
            name=MODEL_NAME,
            ## TODO implement the factory initialize agent here
            python_model="business_customer_loan_validation.py",
            input_example=data_example,
            pip_requirements="requirements.txt"
        )

    mv = mlflow.register_model(name=MODEL_NAME, model_uri=model_info.model_uri)
    client.set_registered_model_alias(
        MODEL_NAME, MODEL_VERSION_ALIAS, mv.version
    )

    rm = client.get_registered_model(MODEL_NAME)
    print_model_info(rm)

    loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)
    result = loaded_model.predict(
        data=data_example
    )

    print("=" * 10, "SANITY CHECK", "=" * 10)
    print(result)
    print("=" * 30)


def destroy(version):
    try:
        client.delete_model_version(name=MODEL_NAME, version=version)
        print(f"Deleted model version {version}")
    except MlflowException:
        print(f"Model version {version} not found.")


def main():
    commands = ["show", "deploy", "destroy"]
    if len(sys.argv) < 2:
        print(f"Args be {commands} python3 main.py deploy_model")
        sys.exit(1)
    command = sys.argv[1]
    match command:
        case "show":
            show()
        case "deploy":
            deploy()
        case "destroy":
            version = sys.argv[2]
            destroy(version)
        case _:
            print(f"Command not found: {command}")


if __name__ == "__main__":
    main()
