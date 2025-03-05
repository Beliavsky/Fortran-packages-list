#!/usr/bin/env python3

"""
name     : xfpm_c.py
source   : https://github.com/Beliavsky/Fortran-packages-list
author   : Beliavsky, Norwid Behrnd
license  : MIT
last edit: [2024-05-07 Tue]
purpose  : report projects that can be built with the Fortran Package Manager
"""

import argparse
import datetime
import os
import re

from time import perf_counter
from urllib3.util import Retry

import requests
from requests.adapters import HTTPAdapter

os.environ["PYTHONIOENCODING"] = "utf-8"


def get_args():
    """get the command-line arguments"""

    parser = argparse.ArgumentParser(
        description="""List projects, organized by topic, that can be built with
        the Fortran Package Manager.  For this, file README.md of project
        'Directory of Fortran codes on GitHub' curated by Beliavsky et al. (see
        https://github.com/Beliavsky/Fortran-code-on-GitHub) is processed as
        input for this script.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        help="said README.md file",
        metavar="FILE",
        type=argparse.FileType("rt", encoding="utf-8"),
        default=None,
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="activate the scripts internal debugger",
        action="store_true",
    )

    parser.add_argument(
        "-t",
        "--test",
        help="constrain a test run to 125 lines output",
        action="store_true",
    )

    return parser.parse_args()


def check_url_exists(url, max_redirects=20, max_retries=5):
    """check accessibility of queried url"""

    session = requests.Session()
    retries = Retry(
        total=max_retries, backoff_factor=1.1, status_forcelist=[500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        # Make a HEAD request to get headers and avoid downloading the content
        # https://stackoverflow.com/questions/46016004/how-to-handle-timeout-error-in-request-headurl
        response = requests.head(url, allow_redirects=True, timeout=5)
        # Check if the response status code is in the range of 200-299 (success)
        if response.status_code in range(200, 300):
            return True, response.status_code
        else:
            return False, response.status_code
    except requests.RequestException as e:
        # Handle exceptions like network errors, invalid URLs, etc.
        return False, str(e)


def file_reader(infile="", debug=False, test=False):
    """iterate on the input file till reaching the threshold"""

    max_lines = 300 if test else 10**6  # allow a constrained test run
    raw_data = [line.strip() for line in infile]
    array_prior_test_condition = len(raw_data)

    if test:
        raw_data = raw_data[:max_lines]
    array_after_test_condition = len(raw_data)

    if debug:
        print("lines in raw_data to process:")
        print(f"array_prior_test_condition: {array_prior_test_condition}")
        print(f"array_after_test_condition: {array_after_test_condition}")

        pattern = re.compile("^\[")  # signature of project lines in raw_data
        projects = list(filter(pattern.match, raw_data))
        print(f"up to {len(projects)} projects to consider\n")

    return raw_data


def checker(text, debug=False):
    """extract the address, report if fpm.toml file is present"""
    # text in parentheses after first after first set of brackets
    match = re.search(r"\[.*?\]\((.*?)\)", text)
    # Extract the match, if it exists
    extracted_address = match.group(1) if match else None
    if extracted_address:
        if debug:
            print("".join([text.strip(), "\n"]))
            print(f"url: {extracted_address}\n")
        fpm_link = extracted_address + "/blob/master/fpm.toml"
        exists, status_or_error = check_url_exists(fpm_link)
        if exists:
            try:
                single_test = "".join([text, "\n"])
                return single_test
            except UnicodeEncodeError as e:
                # Handle the error: for example, print a placeholder text or
                # encode the text in 'utf-8' and print
                print("An encoding error occurred: ", e)
            if debug:
                print(fpm_link)


def triage_lines(raw_data, debug=False):
    """identify lines with addresses to check on GitHub for a fpm.toml file"""
    previous_section_title = ""
    intermediate_register = []

    for i, line in enumerate(raw_data):
        # lines with less work ahead:
        if line.startswith("## Fortran code on GitHub"):
            print("".join([line, "\n"]))
        if line.startswith("* ["):
            print("".join([line, "\n"]))

        # lines with more work ahead
        # projects eventually to visit on GitHub
        if line.startswith("["):
            intermediate_register.append(line)

        # sections like "Art and Music", "Astronomy and Astrophysics", etc.
        if line.startswith("##"):
            if line.startswith("## Fortran code on GitHub") is False:
                if intermediate_register:

                    if debug:
                        print(f"{len(intermediate_register)} entries to check")

                    affirmative_tests = []
                    for entry in intermediate_register:
                        test = checker(entry, debug)
                        if test is not None:
                            affirmative_tests.append(test)
                    if affirmative_tests:
                        print("".join([previous_section_title, "\n"]))
                        affirmative_tests = sorted(affirmative_tests, key=str.casefold)
                        for entry in affirmative_tests:
                            print(entry)
                    intermediate_register = []

                previous_section_title = line

        # Equally report a section if a line about a project happens to be the
        # ultimate line of the raw_data read:
        if i == len(raw_data) - 1:
            if debug:
                print(f"{len(intermediate_register)} entries to check")

            affirmative_tests = []
            for entry in intermediate_register:
                test = checker(entry, debug)
                if test is not None:
                    affirmative_tests.append(test)
            if affirmative_tests:
                print("".join([previous_section_title, "\n"]))
                for entry in affirmative_tests:
                    print(entry)


def main():
    """join the functionalities"""

    args = get_args()
    infile = args.file
    debugger_level = args.debug
    test_level = args.test

    start = perf_counter()
    raw_data = file_reader(infile, debugger_level, test_level)
    triage_lines(raw_data, debugger_level)
    end = perf_counter()

    print(f"last update: {datetime.date.today()}")
    print(f"time elapsed (s): {(end - start):.2f}")


if __name__ == "__main__":
    main()
