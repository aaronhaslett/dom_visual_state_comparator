import os

import yaml

from url_validator import string_is_url

CAPTURE_DIR_NAME = "captures"
CAPTURE_DIR = os.path.join(os.path.dirname(__file__), CAPTURE_DIR_NAME)
SPEC_FILENAME = "capture_spec.yml"
URLS_YML_SECTION_NAME = "urls"


def get_spec(capture_spec_name):
    if not os.path.exists(CAPTURE_DIR):
        print("No capture dir")
        exit(1)

    if not os.path.isdir(CAPTURE_DIR):
        print(
            "ERROR: {} is a file rather than a dir for some reason. Exiting.".format(
                CAPTURE_DIR
            )
        )
        exit(1)

    capture_spec_dir = os.path.join(CAPTURE_DIR, capture_spec_name)

    if not os.path.exists(capture_spec_dir):
        print(
            "ERROR: Capture dir is initialised but capture spec {} doesn't exist.".format(
                capture_spec_name
            )
        )
        exit(1)

    capture_spec_filename = os.path.join(capture_spec_dir, SPEC_FILENAME)

    if not os.path.exists(capture_spec_filename):
        print(
            "ERROR: Dir exists for capture spec {} exists but there's no {} file.".format(
                capture_spec_name, SPEC_FILENAME
            )
        )
        exit(1)

    spec = {}
    with open(capture_spec_filename, "r") as f:
        spec = yaml.full_load(f)

    if not spec:
        print(
            "ERROR: Spec is empty or load failed for spec file {}".format(
                capture_spec_filename
            )
        )
        exit(1)

    if not URLS_YML_SECTION_NAME in spec:
        print(
            "ERROR: {} section not found in spec file {}".format(
                URLS_YML_SECTION_NAME, capture_spec_filename
            )
        )
        exit(1)

    urls = spec["urls"]

    if type(urls) is not list:
        print(
            "ERROR: {} section in spec file {} isn't a list".format(
                URLS_YML_SECTION_NAME, capture_spec_filename
            )
        )
        exit(1)

    if len(urls) == 0 or any(not url for url in urls):
        print(
            "ERROR: {} section in spec file {} is empty or has empty entries".format(
                URLS_YML_SECTION_NAME, capture_spec_filename
            )
        )
        exit(1)

    non_urls = [url for url in urls if not string_is_url(url)]
    if non_urls:
        print("ERROR: Spec has invalid URLs: {}".format(", ".join(non_urls)))
        exit(1)

    return spec, capture_spec_dir
