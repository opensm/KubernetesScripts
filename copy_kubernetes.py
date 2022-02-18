from __future__ import print_function
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
import base64
from kubernetes.client import V1DeploymentList, V1Deployment, V1SecretList, V1Secret, V1ServiceList, V1Service, \
    V1IngressList, V1Ingress, V1ConfigMapList, V1ConfigMap

from random import choice
import string


def gen_password(length=24, chars=string.ascii_letters + string.digits):
    return ''.join([choice(chars) for i in range(length)])


class KubernetesClass:
    def __init__(self):
        self.configuration = kubernetes.client.Configuration()
        self.configuration_create = kubernetes.client.Configuration()
        self._api = None
        self._api_create = None

    def connect(self, auth_host, auth_port, auth_key, api_version):
        """
        :param auth_host:
        :param auth_port:
        :param auth_key:
        :param api_version:
        :return:
        """
        try:
            self.configuration.api_key = {"authorization": "Bearer {}".format(auth_key)}
            self.configuration.host = "https://{}:{}".format(auth_host, auth_port)
            self.configuration.verify_ssl = False
            self.configuration.debug = False
            api_client = kubernetes.client.ApiClient(self.configuration)
            self._api = api_version(api_client)
            print("认证成功!")
            return True
        except Exception as error:
            print("认证异常！{}".format(error))
            return False

    def connect_create(self, auth_host, auth_port, auth_key, api_version):
        """
        :param auth_host:
        :param auth_port:
        :param auth_key:
        :param api_version:
        :return:
        """
        try:
            self.configuration_create.api_key = {"authorization": "Bearer {}".format(auth_key)}
            self.configuration_create.host = "https://{}:{}".format(auth_host, auth_port)
            self.configuration_create.verify_ssl = False
            self.configuration_create.debug = False
            api_client = kubernetes.client.ApiClient(self.configuration_create)
            self._api_create = api_version(api_client)
            print("认证成功!")
            return True
        except Exception as error:
            print("认证异常！{}".format(error))
            return False

    def list_deployment(self, namespace):
        """
        :param namespace:
        :return:
        """
        pretty = 'true'
        allow_watch_bookmarks = True
        limit = 56
        timeout_seconds = 56
        # watch = True

        try:
            api_response = self._api.list_namespaced_deployment(
                namespace, pretty=pretty,
                allow_watch_bookmarks=allow_watch_bookmarks,
                limit=limit,
                timeout_seconds=timeout_seconds
            )
            return api_response
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)

    @staticmethod
    def format_deployment(deployments: V1DeploymentList):
        """
        :return:
        """
        all_deploy = list()
        for deploy in deployments.items:
            deploy_name = deploy.metadata.name
            deployment = V1Deployment()
            deployment.metadata = {
                'namespace': deploy.metadata.namespace.replace('staging', 'prod'),
                'name': deploy.metadata.name,
            }
            container_list = list()
            for x in deploy.spec.template.spec.containers:
                env_list = list()
                container = x
                if not x.env_from:
                    continue
                for y in x.env_from:
                    each_line = y
                    if not y.secret_ref:
                        continue
                    each_line.secret_ref.name = y.secret_ref.name.replace('staging', 'prod')
                    env_list.append(each_line)
                if not env_list:
                    env_list = None
                container.env_from = env_list
                container_list.append(container)
            deployment.spec = {
                'replicas': 2,
                'selector': deploy.spec.selector,
                'template': {
                    'metadata': {
                        'labels': {
                            'app': deploy_name
                        }
                    },
                    'spec': deploy.spec.template.spec
                }
            }
            all_deploy.append(deployment)
        return all_deploy

    def create_deployments(self, deployments: list, namespace: str):
        """
        :param deployments:
        :param namespace:
        :return:
        """
        namespace = namespace.replace('staging', 'prod')
        for x in deployments:
            try:
                api_response = self._api_create.create_namespaced_deployment(namespace, x)
                pprint(api_response)
            except ApiException as e:

                print("Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e)

    def list_secret(self, namespace):
        """
        :param namespace:
        :return:
        """
        try:
            api_response = self._api.list_namespaced_secret(
                namespace
            )
            return api_response
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_secret: %s\n" % e)

    @staticmethod
    def format_secret(secrets: V1SecretList):
        """
        :param secrets:
        :return:
        """
        secret_list = list()
        for secret in secrets.items:
            if 'jenkins' in secret.metadata.name:
                continue
            secret_data = V1Secret()
            secret_dict = dict()
            for x in secret.data:
                db_passwd = gen_password()
                if x == 'elastic_hosts':
                    secret_dict[x] = bytes.decode(base64.b64encode(''.encode("utf-8")))
                elif x == 'elastic_user':
                    secret_dict[x] = bytes.decode(base64.b64encode(''.encode("utf-8")))
                elif x == 'elastic_passwd':
                    secret_dict[x] = bytes.decode(base64.b64encode(''.encode("utf-8")))
                elif x == 'kafka_servers':
                    secret_dict[x] = bytes.decode(base64.b64encode(''.encode("utf-8")))
                elif x == 'mongo_hosts':
                    secret_dict[x] = bytes.decode(base64.b64encode(''.encode("utf-8")))
                elif x == 'mongo_user':
                    secret_dict[x] = bytes.decode(base64.b64encode(
                        "{}_user".format(secret.metadata.name.split('_')[0]).encode("utf-8")))
                elif x == 'mongo_passwd':
                    secret_dict[x] = bytes.decode(base64.b64encode(db_passwd.encode("utf-8")))
                elif x == 'replicaset':
                    secret_dict[x] = bytes.decode(base64.b64encode(''.encode("utf-8")))
                elif x == 'mysql_passwd':
                    secret_dict[x] = bytes.decode(base64.b64encode(db_passwd.encode("utf-8")))
                elif x == 'mysql_port':
                    secret_dict[x] = bytes.decode(base64.b64encode("".encode("utf-8")))
                elif x == 'mysql_user':
                    secret_dict[x] = bytes.decode(base64.b64encode(
                        "{}_user".format(secret.metadata.name.split('_')[0]).encode("utf-8")
                    ))
                elif x == 'redis_passwd':
                    secret_dict[x] = bytes.decode(base64.b64encode("".encode("utf-8")))
                elif x == 'redis_host':
                    secret_dict[x] = bytes.decode(base64.b64encode("".encode("utf-8")))
                elif x == 'redis_port':
                    secret_dict[x] = bytes.decode(base64.b64encode("".encode("utf-8")))
                else:
                    secret_dict[x] = secret.data[x]
            secret_data.data = secret_dict
            secret_data.metadata = {
                'name': secret.metadata.name.replace('staging', 'prod'),
                'namespace': secret.metadata.namespace.replace('staging', 'prod')
            }
            secret_data.type = secret.type
            secret_data.api_version = 'v1'
            secret_data.kind = 'Secret'
            secret_list.append(secret_data)
        return secret_list

    def create_secret(self, secretes: list, namespace: str):
        """
        :param secretes:
        :param namespace:
        :return:
        """
        namespace = namespace.replace('staging', 'prod')
        for secret in secretes:
            try:
                api_response = self._api_create.create_namespaced_secret(namespace, secret)
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)

    def list_service(self, namespace):
        """
        :param namespace:
        :return:
        """
        try:
            api_response = self._api.list_namespaced_service(namespace)
            return api_response
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_service: %s\n" % e)

    def format_service(self, services: V1ServiceList):
        """
        :param services:
        :return:
        """
        service_list = list()
        for service in services.items:
            service_data = V1Service()
            service_data.api_version = 'v1'
            service_data.kind = 'Service'
            service_data.spec = {
                'ports': service.spec.ports,
                'selector': service.spec.selector,
                'type': service.spec.type
            }
            service_data.metadata = {
                'name': service.metadata.name,
                'namespace': service.metadata.namespace.replace('staging', 'prod')
            }
            service_list.append(service_data)
        return service_list

    def create_service(self, services: list, namespace: str):
        """
        :param services:
        :param namespace:
        :return:
        """
        namespace = namespace.replace('staging', 'prod')
        for x in services:
            try:
                api_response = self._api_create.create_namespaced_service(
                    namespace, x
                )
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

    def list_ingress(self, namespace):
        """
        :param namespace:
        :return:
        """
        try:
            api_response = self._api.list_namespaced_ingress(namespace)
            return api_response
        except ApiException as e:
            print("Exception when calling NetworkingV1Api->list_namespaced_ingress: %s\n" % e)

    def format_ingress(self, ingresses: V1IngressList):
        """
        :param ingresses:
        :return:
        """
        ingress_list = list()
        for ingress in ingresses.items:
            ingress_data = V1Ingress()
            ingress_data.api_version = 'networking.k8s.io/v1'
            ingress_data.kind = 'Ingress'
            if 'nginx.ingress.kubernetes.io/rewrite-target' in ingress.metadata.annotations.keys():
                ingress_data.metadata = {
                    'name': ingress.metadata.name,
                    'namespace': ingress.metadata.namespace.replace('staging', 'prod'),
                    'annotations': {
                        'kubernetes.io/ingress.class': 'nginx',
                        'nginx.ingress.kubernetes.io/rewrite-target': ingress.metadata.annotations[
                            'nginx.ingress.kubernetes.io/rewrite-target']}
                }
            else:
                ingress_data.metadata = {
                    'name': ingress.metadata.name,
                    'namespace': ingress.metadata.namespace.replace('staging', 'prod'),
                    'annotations': {'kubernetes.io/ingress.class': 'nginx'}
                }
            ingress_data.spec = ingress.spec
            hosts = list()
            for w in ingress.spec.rules:
                w.host = w.host.replace('staging', 'prod')
                hosts.append(w)
            ingress_data.spec = {'rules': hosts}
            ingress_list.append(ingress_data)
        return ingress_list

    def create_ingress(self, ingresses: list, namespace: str):
        """
        :param ingresses:
        :param namespace:
        :return:
        """
        namespace = namespace.replace('staging', 'prod')
        for x in ingresses:
            print(x)
            try:
                api_response = self._api_create.create_namespaced_ingress(namespace, x)
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling NetworkingV1Api->create_namespaced_ingress: %s\n" % e)

    def list_configmap(self, namespace):
        """
        :param namespace:
        api :CoreV1Api
        :return:
        """
        try:
            api_response = self._api.list_namespaced_config_map(namespace)
            return api_response
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)

    def format_configmap(self, configmaps: V1ConfigMapList):
        """
        :param configmaps:
        :return:
        """
        configmap_list = list()
        for configmap in configmaps.items:
            configmap_data = V1ConfigMap()
            configmap_data.api_version = 'v1'
            configmap_data.kind = 'ConfigMap'
            config_data = dict()
            for k, v in configmap.data.items():
                config_data[k] = v.replace('staging', 'prod')
            configmap_data.data = config_data
            configmap_data.metadata = {
                'name': configmap.metadata.name.replace('staging', 'prod'),
                'namespace': configmap.metadata.namespace.replace('staging', 'prod')
            }
            configmap_list.append(configmap_data)
        return configmap_list

    def create_configmap(self, configmaps: list, namespace):
        """
        :param configmaps:
        :param namespace:
        :return:
        """
        namespace = namespace.replace('staging', 'prod')
        for x in configmaps:
            try:
                api_response = self._api_create.create_namespaced_config_map(namespace, x)
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling CoreV1Api->create_namespaced_config_map: %s\n" % e)


def secret_create(namespace):
    """
    :param namespace:
    :return:
    """
    version = kubernetes.client.CoreV1Api
    staging_k.connect(auth_host=staging_host, auth_port=staging_port, auth_key=staging_key, api_version=version)
    data = staging_k.list_secret(namespace=namespace)
    format_data = staging_k.format_secret(secrets=data)
    prod_k.connect_create(auth_host=prod_host, auth_port=prod_port, auth_key=prod_key, api_version=version)
    prod_k.create_secret(secretes=format_data, namespace=namespace)


def configmap_create(namespace):
    """
    :param namespace:
    :return:
    """
    version = kubernetes.client.CoreV1Api
    staging_k.connect(auth_host=staging_host, auth_port=staging_port, auth_key=staging_key, api_version=version)
    data = staging_k.list_configmap(namespace=namespace)
    format_data = staging_k.format_configmap(configmaps=data)
    prod_k.connect_create(auth_host=prod_host, auth_port=prod_port, auth_key=prod_key, api_version=version)
    prod_k.create_configmap(configmaps=format_data, namespace=namespace)


def service_create(namespace):
    """
    :param namespace:
    :return:
    """
    version = kubernetes.client.CoreV1Api
    staging_k.connect(auth_host=staging_host, auth_port=staging_port, auth_key=staging_key, api_version=version)
    data = staging_k.list_service(namespace=namespace)
    format_data = staging_k.format_service(services=data)
    prod_k.connect_create(auth_host=prod_host, auth_port=prod_port, auth_key=prod_key, api_version=version)
    prod_k.create_service(services=format_data, namespace=namespace)


def ingress_create(namespace):
    """
    :param namespace:
    :return:
    """
    version = kubernetes.client.NetworkingV1Api
    staging_k.connect(auth_host=staging_host, auth_port=staging_port, auth_key=staging_key, api_version=version)
    data = staging_k.list_ingress(namespace=namespace)
    format_data = staging_k.format_ingress(ingresses=data)
    prod_k.connect_create(auth_host=prod_host, auth_port=prod_port, auth_key=prod_key, api_version=version)
    prod_k.create_ingress(ingresses=format_data, namespace=namespace)


def deployment_create(namespace):
    """
    :param namespace:
    :return:
    """
    version = kubernetes.client.AppsV1Api
    staging_k.connect(auth_host=staging_host, auth_port=staging_port, auth_key=staging_key, api_version=version)
    data = staging_k.list_deployment(namespace=namespace)
    format_data = staging_k.format_deployment(deployments=data)
    prod_k.connect_create(auth_host=prod_host, auth_port=prod_port, auth_key=prod_key, api_version=version)
    prod_k.create_deployments(deployments=format_data, namespace=namespace)


staging_key = ""
staging_host = ""
staging_port = 5443
prod_key = ""
prod_host = "127.0.0.1"
prod_port = 5443
staging_k = KubernetesClass()
prod_k = KubernetesClass()

name_space = ''

service_create(namespace=name_space)
secret_create(namespace=name_space)
configmap_create(namespace=name_space)
ingress_create(namespace=name_space)
deployment_create(namespace=name_space)
