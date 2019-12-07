# Amy

[![Build Status](https://travis-ci.org/best-doctor/Amy.svg?branch=master)](https://travis-ci.org/best-doctor/Amy)
[![Maintainability](https://api.codeclimate.com/v1/badges/e12619d2003e8919c256/maintainability)](https://codeclimate.com/github/best-doctor/Amy/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/e12619d2003e8919c256/test_coverage)](https://codeclimate.com/github/best-doctor/Amy/test_coverage)

Set of scripts for codereview flow with Jira, Slack and GitLab.

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
