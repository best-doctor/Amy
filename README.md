# Amy

[![Build Status](https://travis-ci.org/best-doctor/Amy.svg?branch=master)](https://travis-ci.org/best-doctor/Amy)
[![Maintainability](https://api.codeclimate.com/v1/badges/e12619d2003e8919c256/maintainability)](https://codeclimate.com/github/best-doctor/Amy/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/e12619d2003e8919c256/test_coverage)](https://codeclimate.com/github/best-doctor/Amy/test_coverage)

Set of scripts for codereview flow with Jira, Slack and GitLab.

![Amy](https://raw.githubusercontent.com/best-doctor/Amy/master/docs_imgs/amy.jpg)

## Installation

- `git clone`
- `pip install -r requirements.txt`
- `cp .env.example .env`
- fill in all vars in `.env` file
- touch `src/local_config.py`
- fill in `PROJECTS_INFO`, `DEVELEOPERS_INFO`
  and `REPO_TO_CODETYPE_MAPPING` in `src/local_config.py`

## Usage

- `python waf.py` – for debug usage
- `DOGGIE_DEBUG=False python waf.py` – for prod usage (writes to all channels)

## Contributing

We would love you to contribute to our project. It's simple:

1. Create an issue with bug you found or proposal you have.
   Wait for approve from maintainer.
1. Create a pull request. Make sure all checks are green.
1. Fix review comments if any.
1. Be awesome.

Here are useful tips:

- You can run all checks and tests with `make check`.
  Please do it before TravisCI does.
- We use [BestDoctor python styleguide](https://github.com/best-doctor/guides/blob/master/guides/en/python_styleguide.md).
- We respect [Django CoC](https://www.djangoproject.com/conduct/).
  Make soft, not bullshit.
