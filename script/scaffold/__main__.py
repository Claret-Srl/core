"""Validate manifests."""
import argparse
from pathlib import Path
import subprocess
import sys

from . import docs, error, gather_info, generate
from .const import COMPONENT_DIR

TEMPLATES = [
    p.name for p in (Path(__file__).parent / "templates").glob("*") if p.is_dir()
]


def valid_integration(integration):
    """Test if it's a valid integration."""
    if not (COMPONENT_DIR / integration).exists():
        raise argparse.ArgumentTypeError(
            f"The integration {integration} does not exist."
        )

    return integration


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser(description="Safegate Pro Scaffolder")
    parser.add_argument("template", type=str, choices=TEMPLATES)
    parser.add_argument(
        "--develop", action="store_true", help="Automatically fill in info"
    )
    parser.add_argument(
        "--integration", type=valid_integration, help="Integration to target."
    )

    arguments = parser.parse_args()

    return arguments


def main():
    """Scaffold an integration."""
    if not Path("requirements_all.txt").is_file():
        print("Run from project root")
        return 1

    args = get_arguments()

    info = gather_info.gather_info(args)
    print()

    # If we are calling scaffold on a non-existing integration,
    # We're going to first make it. If we're making an integration,
    # we will also make a config flow to go with it.

    if info.is_new:
        generate.generate("integration", info)

        # If it's a new integration and it's not a config flow,
        # create a config flow too.
        if not args.template.startswith("config_flow"):
            if info.oauth2:
                template = "config_flow_oauth2"
            elif info.authentication or not info.discoverable:
                template = "config_flow"
            else:
                template = "config_flow_discovery"

            generate.generate(template, info)

    # If we wanted a new integration, we've already done our work.
    if args.template != "integration":
        generate.generate(args.template, info)

    pipe_null = {} if args.develop else {"stdout": subprocess.DEVNULL}

    print("Running hassfest to pick up new information.")
    subprocess.run(["python", "-m", "script.hassfest"], **pipe_null)
    print()

    print("Running gen_requirements_all to pick up new information.")
    subprocess.run(["python", "-m", "script.gen_requirements_all"], **pipe_null)
    print()

    print("Running script/translations_develop to pick up new translation strings.")
    subprocess.run(
        [
            "python",
            "-m",
            "script.translations",
            "develop",
            "--integration",
            info.domain,
        ],
        **pipe_null,
    )
    print()

    if args.develop:
        print("Running tests")
        print(f"$ pytest -vvv tests/components/{info.domain}")
        subprocess.run(["pytest", "-vvv", f"tests/components/{info.domain}"])
        print()

    docs.print_relevant_docs(args.template, info)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except error.ExitApp as err:
        print()
        print(f"Fatal Error: {err.reason}")
        sys.exit(err.exit_code)
