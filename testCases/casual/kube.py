#!/usr/bin/env python3

import locust
import argparse
import importlib.util
import secrets
import shutil
import subprocess
import sys
import yaml

from kubernetes import client, config, watch
from pathlib import Path


config.load_kube_config()
core_api = client.CoreV1Api()
apps_api = client.AppsV1Api()
batch_api = client.BatchV1Api()

def _create_namespace_object(name: str):
    ns = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
    return ns

def _create_deployment_object(name: str, image: str):
    container = client.V1Container(
        name=name,
        image=image,
        image_pull_policy='Always',
        volume_mounts=[
            client.V1VolumeMount(name='domain-config', mount_path='/home/casual/configuration/domain.yaml', sub_path='domain.yaml')
        ]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': name}),
        spec=client.V1PodSpec(
            containers=[container],
            volumes=[client.V1Volume(name='domain-config', config_map=client.V1ConfigMapVolumeSource(name=f'{name}-config'))]
        )
    )
    spec = client.V1DeploymentSpec(
        template=template,
        selector={'matchLabels': {'app': name}}
    )
    deployment = client.V1Deployment(
        api_version='apps/v1',
        kind='Deployment',
        metadata=client.V1ObjectMeta(name=name),
        spec=spec,
    )

    return deployment


def _create_service_object(name):
    svc = client.V1Service(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1ServiceSpec(
            ports=[
                client.V1ServicePort(port=7772, target_port=7772, name='casual'),
                client.V1ServicePort(port=8080, target_port=8080, name='http')
            ],
            selector={'app': name}
        ))
    return svc


def _create_pvc_object(name):
    pass


def _create_configmap_object(name, data):
    cm = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name=name),
        data=data
    )
    return cm


def _create_job_object(name, image):
    container = client.V1Container(
        name=name,
        image=image,
        image_pull_policy='Always',
        command=['/bin/bash', '-c', 'casual domain -b configuration/*.yaml && source /home/casual/venv/bin/activate && python3 /home/casual/runner.py'],
        volume_mounts=[
            client.V1VolumeMount(name='domain-config', mount_path='/home/casual/configuration/domain.yaml', sub_path='domain.yaml'),
            client.V1VolumeMount(name='testcase-script', mount_path='/home/casual/python/testcase.py', sub_path='testcase.py'),
            client.V1VolumeMount(name='testcase-parameters', mount_path='/home/casual/test/parameters.yaml', sub_path='parameters.yaml')
        ]
    )
    
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': name}),
        spec=client.V1PodSpec(
            restart_policy="Never",
            containers=[container],
            volumes=[
                client.V1Volume(name='domain-config', config_map=client.V1ConfigMapVolumeSource(name=f'{name}-config')),
                client.V1Volume(name='testcase-script', config_map=client.V1ConfigMapVolumeSource(name=f'{name}-script')),
                client.V1Volume(name='testcase-parameters', config_map=client.V1ConfigMapVolumeSource(name=f'{name}-parameters'))
            ]
        )
    )

    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    return job


def create_namespace(name: str):
    field_selector = f'metadata.name={name}'
    if len(core_api.list_namespace(field_selector=field_selector).items) == 0:
        ns = _create_namespace_object(name)
        core_api.create_namespace(ns)


def create_configmap(namespace: str, name: str, data: dict):
    cm = _create_configmap_object(name, data)
    core_api.create_namespaced_config_map(namespace=namespace, body=cm)


def create_deployment(namespace: str, name: str, image: str):
    dp = _create_deployment_object(name, image)
    svc = _create_service_object(name)

    core_api.create_namespaced_service(namespace=namespace, body=svc)
    apps_api.create_namespaced_deployment(namespace=namespace, body=dp)


def create_job(namespace: str, name: str, image: str):
    job = _create_job_object(name, image)
    batch_api.create_namespaced_job(namespace=namespace, body=job)


def wait_for_deployment(namespace: str, name: str, timeout = 30) -> str | None:
    w = watch.Watch()
    for event in w.stream(func=core_api.list_namespaced_pod,
                          namespace=namespace,
                          label_selector=f'app={name}',
                          timeout_seconds=timeout):
        if event["object"].status.phase == "Running":
            w.stop()
            return event["object"].metadata.name

    return None

def wait_for_job(namespace: str, name: str, timeout) -> str | None:
    w = watch.Watch()
    for event in w.stream(func=batch_api.list_namespaced_job,
                          namespace=namespace,
                          timeout_seconds=timeout):
        if event['object'].status.succeeded:
            w.stop()
            return event["object"].metadata.name

    return None


def get_job_pod(namespace: str, job_name: str) -> str:
    # fixme: we only expect a single result, should enforce this better
    pod_list = core_api.list_namespaced_pod(namespace=namespace, label_selector=f'job-name={job_name}')
    return pod_list.items[0].metadata.name


def get_remote_file(namespace: str, name: str, filename: str, destdir: str):
    rc = subprocess.run(f'kubectl cp -n {namespace} {name}:/home/casual/{filename} {destdir}/{namespace}/{name}/{filename}', shell=True)
    pass


default_parameters = {
    "runtime": 60
}

def collect_parameters(param_list: list[str]):
    print(param_list)
    parameters = default_parameters
    for key_value in param_list:
        key, value = tuple(key_value.split("="))
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        parameters[key] = value

    print(f"parameters: {parameters}")
    return parameters


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="Python file with testcase")
    parser.add_argument('-p', '--parameters', dest="parameters", default=[], required=False, nargs=1, action='extend', help="Add testcase parameters (key=value)")
    parser.add_argument('--image', default='oscc1:30000/casual-performance:1.7.8')
    parser.add_argument('-o', '--output-name', default='result')
    parser.add_argument('--zip-results', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    parameters = collect_parameters(args.parameters)

    # Generate a namespace name
    namespace = f'performance-{secrets.token_hex(6)}'
    create_namespace(namespace)
    print(f'Namespace: {namespace} created')

    # load/import python testcase file
    spec = importlib.util.spec_from_file_location('testcase', args.file)
    if spec is None:
        print("Failed to load/import python testcase.")
        sys.exit(1)
    
    testcase = importlib.util.module_from_spec(spec)
    sys.modules['testcase'] = testcase
    spec.loader.exec_module(testcase)

    # generate domains
    domains = testcase.get_domains(parameters)
    for name, config in domains.items():
        if name != 'runner':
            create_configmap(namespace=namespace, name=f'{name}-config', data={'domain.yaml': config.as_yaml()})
            create_deployment(namespace=namespace, name=name, image=args.image)
            print(f'Created domain: {name}')

    started_domains = []

    # wait for all domains
    for name, config in domains.items():
        if name != 'runner':
            print(f'Waiting for {name} ...')
            pod_name = wait_for_deployment(namespace=namespace, name=name)
            if pod_name is not None:
                print(f'Started pod: {pod_name}')
                started_domains.append(pod_name)

    # create job to run test
    runner_config = domains['runner']
    file_path = Path(args.file)
    with file_path.open() as file:
        file_contents = file.read()
        create_configmap(namespace=namespace, name=f'runner-config', data={'domain.yaml': runner_config.as_yaml()})
        create_configmap(namespace=namespace, name=f'runner-parameters', data={'parameters.yaml': yaml.safe_dump(parameters)})
        create_configmap(namespace=namespace, name=f'runner-script', data={'testcase.py': file_contents})
        print(f'Creating job: runner')
        create_job(namespace=namespace, name='runner', image='oscc1:30000/casual-performance:1.7.8')

    job_name = wait_for_job(namespace=namespace, name=name, timeout=2 * parameters.get('runtime',30))
    if job_name is not None:
        print(f'Job completed: {job_name}')
        # Ooops, cannot get file from completed pod...
        # get_remote_file(namespace, get_job_pod(namespace, job_name), 'logs', destdir=args.output_name)

    # get all results
    for name  in started_domains:
        get_remote_file(namespace, name, 'logs', destdir=args.output_name)
    

    if args.zip_results:    
        shutil.make_archive(args.output_name, 'zip', args.output_name)
        shutil.rmtree(args.output_name)

if __name__ == '__main__':
    main()