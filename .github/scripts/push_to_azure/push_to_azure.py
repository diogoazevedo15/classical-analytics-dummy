#!/usr/bin/env python3

"""
This script is used to deploy environments and components to Azure Machine Learning
either in a workspace or a shared registry mode. It authenticates using Azure credentials
and deploys components and environments based on the configuration files found in specified directories.
"""

import logging
import os
import sys
from pathlib import Path

from azure.ai.ml import MLClient, load_component, load_environment
from azure.identity import ClientSecretCredential

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def deploy_environment(
    ml_client: MLClient, env_file: Path, phase_label: str, component_name: str
):
    """
    Deploy (create or update) an environment if env.yaml is found.

    Args:
        ml_client (MLClient): The Azure ML client used for deployment.
        env_file (Path): The path to the environment YAML file.
        phase_label (str): The label indicating the phase (e.g., TRAIN, INFERENCE).
        component_name (str): The name of the component for which the environment is being deployed.
    """
    if not env_file.is_file():
        logging.info(
            f"[{phase_label}] No env.yaml for '{component_name}'. Skipping environment."
        )
        return

    logging.info(f"[{phase_label}] Found environment file: {env_file}")
    try:
        environment = load_environment(env_file)
        ml_client.environments.create_or_update(environment)
        logging.info(
            f"[{phase_label}] ✅ Environment for '{component_name}' deployed successfully.\n"
        )
    except Exception as e:
        logging.error(
            f"[{phase_label}] ❌ Error deploying environment for '{component_name}': {e}"
        )
        sys.exit(1)


def deploy_component_or_pipeline(
    ml_client: MLClient, component_file: Path, phase_label: str, component_name: str
):
    """
    Deploy (create or update) a component (or pipeline component) if config.yaml/pipeline.yaml is found.

    We assume pipeline.yaml or config.yaml are both valid inputs to `load_component(source=...)`.

    Args:
        ml_client (MLClient): The Azure ML client used for deployment.
        component_file (Path): The path to the component or pipeline YAML file.
        phase_label (str): The label indicating the phase (e.g., TRAIN, INFERENCE).
        component_name (str): The name of the component or pipeline being deployed.
    """
    if not component_file.is_file():
        logging.info(
            f"[{phase_label}] No file found for '{component_name}' at {component_file}. Skipping."
        )
        return

    logging.info(f"[{phase_label}] Found component/pipeline file: {component_file}")
    try:
        loaded_comp = load_component(source=component_file)
        ml_client.components.create_or_update(loaded_comp)
        logging.info(
            f"[{phase_label}] ✅ '{component_name}' (component/pipeline) deployed successfully.\n"
        )
    except Exception as e:
        logging.error(f"[{phase_label}] ❌ Error deploying '{component_name}': {e}")
        sys.exit(1)


def main():
    """
    Main function to execute the deployment process. It determines the mode of deployment,
    authenticates using Azure credentials, and deploys environments and components based on
    the specified directories and configuration files.
    """
    # Determine mode: "workspace" or "shared_registry"
    mode = os.getenv("AZURE_MODE", "workspace").strip().lower()

    # Common SP credentials
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    logging.info(f"Using AZURE_MODE: {mode}")
    logging.info("Authenticating with ClientSecretCredential...")

    # Create the credential
    credential = ClientSecretCredential(
        tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
    )

    # Decide how to instantiate MLClient based on mode
    if mode == "shared_registry":
        registry_name = os.getenv("AZURE_REGISTRY_NAME")
        registry_location = os.getenv("AZURE_REGISTRY_LOCATION")

        if not registry_name or not registry_location:
            logging.error(
                "❌ For 'shared_registry' mode, AZURE_REGISTRY_NAME and AZURE_REGISTRY_LOCATION must be set."
            )
            sys.exit(1)

        ml_client = MLClient(
            credential=credential,
            registry_name=registry_name,
            registry_location=registry_location,
        )
        logging.info(
            f"Connected to shared registry: {registry_name} @ {registry_location}"
        )
    else:
        # default to workspace mode
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        workspace_name = os.getenv("AZURE_WORKSPACE_NAME")

        if not subscription_id or not resource_group or not workspace_name:
            logging.error(
                "❌ For 'workspace' mode, you must set AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, and AZURE_WORKSPACE_NAME."
            )
            sys.exit(1)

        ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
        )
        logging.info(
            f"Connected to workspace: {workspace_name} (RG: {resource_group}, Sub: {subscription_id})"
        )

    # =============================
    # TRAIN COMPONENTS & "PIPELINE"
    # =============================
    logging.info("")
    logging.info("#################################################################")
    logging.info("### [TRAIN] Deploying Environments & Components               ###")
    logging.info("#################################################################\n")

    train_components_dir = Path("src/train/components")
    if train_components_dir.is_dir():
        for component_dir in train_components_dir.iterdir():
            if not component_dir.is_dir():
                continue

            component_name = component_dir.name

            logging.info("--------------------------------------------------")
            logging.info(f"[TRAIN] Currently in directory: {component_dir}")
            logging.info(f"[TRAIN] Component name: {component_name}")
            logging.info("--------------------------------------------------")

            deploy_environment(
                ml_client,
                env_file=component_dir / "env.yaml",
                phase_label="TRAIN",
                component_name=component_name,
            )
            deploy_component_or_pipeline(
                ml_client,
                component_file=component_dir / "config.yaml",
                phase_label="TRAIN",
                component_name=component_name,
            )
    else:
        logging.info("[TRAIN] No 'train/components' directory found. Skipping.")

    logging.info("")
    logging.info("#################################################################")
    logging.info("### [TRAIN] Checking for pipeline.yaml as a pipeline component ###")
    logging.info("#################################################################\n")

    train_pipeline_file = Path("src/train/pipeline.yaml")
    if train_pipeline_file.is_file():
        deploy_component_or_pipeline(
            ml_client,
            component_file=train_pipeline_file,
            phase_label="TRAIN",
            component_name="train_pipeline",
        )
    else:
        logging.info("[TRAIN] No pipeline.yaml found in 'src/train'. Skipping.")

    # =============================
    # INFERENCE COMPONENTS & "PIPELINE"
    # =============================
    logging.info("")
    logging.info("#################################################################")
    logging.info("### [INFERENCE] Deploying Environments & Components           ###")
    logging.info("#################################################################\n")

    inference_components_dir = Path("src/inference/components")
    if inference_components_dir.is_dir():
        for component_dir in inference_components_dir.iterdir():
            if not component_dir.is_dir():
                continue

            component_name = component_dir.name

            logging.info("--------------------------------------------------")
            logging.info(f"[INFERENCE] Currently in directory: {component_dir}")
            logging.info(f"[INFERENCE] Component name: {component_name}")
            logging.info("--------------------------------------------------")

            deploy_environment(
                ml_client,
                env_file=component_dir / "env.yaml",
                phase_label="INFERENCE",
                component_name=component_name,
            )
            deploy_component_or_pipeline(
                ml_client,
                component_file=component_dir / "config.yaml",
                phase_label="INFERENCE",
                component_name=component_name,
            )
    else:
        logging.info("[INFERENCE] No 'inference/components' directory found. Skipping.")

    logging.info("")
    logging.info("#################################################################")
    logging.info("### [INFERENCE] Checking for pipeline.yaml as pipeline comp   ###")
    logging.info("#################################################################\n")

    inference_pipeline_file = Path("src/inference/pipeline.yaml")
    if inference_pipeline_file.is_file():
        deploy_component_or_pipeline(
            ml_client,
            component_file=inference_pipeline_file,
            phase_label="INFERENCE",
            component_name="inference_pipeline",
        )
    else:
        logging.info("[INFERENCE] No pipeline.yaml found in 'src/inference'. Skipping.")

    # Done!
    logging.info("✅ All done! Push to Azure completed without errors.")


if __name__ == "__main__":
    main()
