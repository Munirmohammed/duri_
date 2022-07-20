# duri

An implementation of [ga4gh-duri](https://github.com/ga4gh-duri/ga4gh-duri.github.io/tree/master/researcher_ids)

## Documentation : 

see [google-doc](https://docs.google.com/document/d/1HfF6laHF8R3fR7tefsq93dGSD5FNmI03T4dXRehkauY/edit?usp=sharing) which describes the platform

## Getting started

**Devs** - run `make dev`

**Prod** - run `make run-d`

## Documentation

### Workspaces

- only a workspace creator or a workspace member with `admin` membership can create a team or add a member under that workspace
- each workspace must have atleast 1 team , if a workspace is created without a team , a team called default is created for them.

### Users

- a user must belong to atleast 1 workspace and 1 team of that workspace.