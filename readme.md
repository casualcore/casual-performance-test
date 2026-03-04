# Casual performance test

## Requirements

- A kubernetes cluster, accesible with `kubectl`
- docker, to build images
- python3
- suitable private docker repository

## Setup

Setup proper roles and permissions on kubernetes to allow creation of new namespace, pvc's, deployments and jobs

Verify that you can access your kubernetes cluster. Test with `kubectl get nodes`

### Clone repo

### Create virtual environment for python

```
%> python -m venv <env-path>
%> source <env-path>/bin/activate
%> pip install -r requirements.txt
```

### Adjust python path and environment

```
%> export PYTHON_PATH=<path-to-repo>
%> export CASUAL_PERFORMANCE_IMAGE_REPO=<url-to-private-repo>
```

### Build and push image for desired version(s) of casual

```
%> ./build_image.sh 1.8.12
```

## Run tests

Example:

```
%> ./kube.py --image-version 1.8.12 -p runtime=60 testCases/casual/007_queue_forward_local.py
```

This will create a new namespace in your kubernetes cluster that will contain any kubernetes objects created by this testcase.
After the test is done, all log files are extraced from the pods and stored in a zip file named `result.zip` (default behaviour)

Also note that by default this namespace is left intact after the tests are done. If you pass the argument `--clean` to `kube.py` it will be automatically deleted after the test are done.

## Visualization

The output from locust can be visualized with `plot.py output1.zip output2.zip ... outputN.zip`

The output from remote casual domains can be visualized with [`svcplot.py`](visualization/readme.md)

No visualization for other metrics yet.

## Writing test cases

