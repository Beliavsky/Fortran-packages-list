#!/usr/bin/env python3

"""
name     : xfpm.py
source   : https://github.com/Beliavsky/Fortran-packages-list
author   : Beliavsky, Norwid Behrnd
license  : MIT
last edit: 2024-02-27
purpose  : report projects that can be built with the Fortran Package Manager
"""

import argparse
import os
import re
import requests
import time

os.environ['PYTHONIOENCODING'] = 'utf-8'

t0 = time.time()


def get_args():
    """get the command-line arguments"""

    parser = argparse.ArgumentParser(
        description="""List projects, organized by topic, that can be built with
        the Fortran Package Manager.  For this, file README.md of project
        'Directory of Fortran codes on GitHub' curated by Beliavsky et al. (see
        https://github.com/Beliavsky/Fortran-code-on-GitHub) is processed as
        input for this script.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "file",
        help="said README.me file",
        metavar="FILE",
        type=argparse.FileType("rt", encoding="utf-8"),
        default=None)

    parser.add_argument(
        "-d",
        "--debug",
        help="activate the scripts internal debugger",
        action="store_true")

    parser.add_argument(
        "-t",
        "--test",
        help="constrain a test run to 125 lines output",
        action="store_true")

    return parser.parse_args()


def check_url_exists(url):
    """check accessibility of queried url"""
    try:
        # Make a HEAD request to get headers and avoid downloading the content
        response = requests.head(url, allow_redirects=True)
        # Check if the response status code is in the range of 200-299 (success)
        if response.status_code in range(200, 300):
            return True, response.status_code
        else:
            return False, response.status_code
    except requests.RequestException as e:
        # Handle exceptions like network errors, invalid URLs, etc.
        return False, str(e)


def file_reader(infile="", debug=False, test=False):
    """work on the input file"""

    # allow a constrained test run:
    if test:
        max_lines = 125
    else:
        max_lines = 10**6

#    debug = False
#with open(infile, "r", encoding="utf-8") as fp:

    # for i, text in enumerate(fp):
    for i, text in enumerate(infile):
        if i > max_lines:
            break
        if text.startswith("*") or text.startswith("##"): # category marker
            print(text)
            continue
        # text in parentheses after first after first set of brackets
        match = re.search(r'\[.*?\]\((.*?)\)', text) 
        # Extract the match, if it exists
        extracted_text = match.group(1) if match else None
        if extracted_text:
            if debug:
                print("\n", i)
                print(text.strip())
                print(extracted_text)
            fpm_link = extracted_text + "/blob/master/fpm.toml"
            exists, status_or_error = check_url_exists(fpm_link)
            if exists:
                try:
                    print(text)
                except UnicodeEncodeError as e:
                    # Handle the error: for example, print a placeholder text or
                    # encode the text in 'utf-8' and print
                    print("An encoding error occurred: ", e)
                if debug:
                    print(fpm_link)


def main():
    """join the functionalities"""

    args = get_args()
    infile = args.file
    debugger_level = args.debug
    test_level = args.test

    file_reader(infile, debugger_level, test_level)


if __name__ == "__main__":
    main()
# print("time elapsed (s):", "%0.2f"%(time.time() - t0))
