# duri

An implementation of [ga4gh-duri](https://github.com/ga4gh-duri/ga4gh-duri.github.io/tree/master/researcher_ids)

## Services Overview

1. cognito  : user identity pool service
2. [ory-keto](https://www.ory.sh/docs/keto) : access-control engine

## Documentation : 

see [google-doc](https://docs.google.com/document/d/1HfF6laHF8R3fR7tefsq93dGSD5FNmI03T4dXRehkauY/edit?usp=sharing) which describes the platform

## Getting started

**Devs** - run `make dev`

**Prod** - run `make run-d`

## Documentation

### Workspaces

- only a workspace creator or a workspace member with `admin` membership can create a team or add a member under that workspace
- each workspace must have atleast 1 team , if a workspace is created without a team , a team called default is created for them.
- [todo] a workspace can be **private** or **public** . if public users can add thereself to the workspace if private a user can request to be added and admins can accept or revoke the request. Admins can also invite users to a workspace in which-case users can accept or reject the request too.
- [todo] a workspace can be **hidden** , in which-case the workspace will not be visible in the UI for non-members and only the admin can add users to that workspace.
- only users with **admin** membership to a workspace can create teams under that workspace.

### Users

- a user must belong to atleast 1 workspace and 1 team of that workspace.

### Permissions and Roles

Am IAM based permission RBAC-style role-permission model managed by [ory-keto](https://www.ory.sh/docs/keto) dockerized proxy service included in the stack