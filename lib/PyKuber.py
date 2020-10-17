# -*- coding: utf-8 -*-
import base64
import glob
import hashlib
import hmac
import json
import os
import shutil
import sys
import time
import urllib
from xml.dom.minidom import parse

import docker
import requests
import yaml
from kubernetes import config, client

from lib.Log import RecodeLog
from lib.setting import KEY_DIR, \
    WORKSPACE, \
    HARBOR_URL, \
    MIDDLEWARE, \
    DEPLOY_YAML_DIR, \
    SERVICE_YAML_DIR, \
    SRC_POM_DIR, \
    DINGDING_SECRET, \
    DINGDING_TOKEN

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding("utf-8")


class PyKuber:
    def __init__(self):
        self.docker_client = docker.client.from_env()

    @staticmethod
    def login(key_file=os.path.join(KEY_DIR, 'config.yaml')):
        """
        :param key_file:
        :return:
        """
        if not os.path.exists(key_file):
            raise Exception("验证文件不存在:{0}".format(key_file))
        config.load_kube_config(config_file=key_file)

    def check_deploy(self, namespace, env, deploy):
        """
        :param namespace:
        :param env:
        :param deploy:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1 = client.AppsV1Api()
        service_data = v1.list_namespaced_deployment(namespace=namespace)
        service_list = [value.metadata.name for value in service_data.items]
        if deploy in service_list:
            return True
        else:
            return False

    def get_all_service(self, env):
        """
        :param env:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1 = client.CoreV1Api()
        return v1.list_service_for_all_namespaces()

    def check_service(self, namespace, env, service):
        """
        :param namespace:
        :param env:
        :param service:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1 = client.CoreV1Api()
        service_data = v1.list_namespaced_service(namespace=namespace)
        service_list = [value.metadata.name for value in service_data.items]
        if service in service_list:
            return True
        else:
            return False

    def exec_command(self, command):
        """
        :param command:
        :return:
        """
        try:
            if sys.version_info < (3, 0):
                import commands
                (status, output) = commands.getstatusoutput(cmd=command)
            else:
                import subprocess
                (status, output) = subprocess.getstatusoutput(cmd=command)
            if status != 0:
                raise Exception(output)
            RecodeLog.info(msg="执行命令成功：{0}".format(command))
            return True
        except Exception as error:
            RecodeLog.error("执行命令异常：{0},原因:{1}".format(command, error))
            return False

    def get_service_nodeports(self, env):
        """
        :param env:
        :return:
        """
        service_data = self.get_all_service(env=env)
        service_list = [value.spec.ports for value in service_data.items]
        node_port = list()
        for service in service_list:
            for port in service:
                if hasattr(port, 'node_port'):
                    node_port.append(getattr(port, 'node_port'))
                if hasattr(port, 'nodePort'):
                    node_port.append(getattr(port, 'nodePort'))
        return node_port

    def get_service_target_ports(self, env):
        """
        :param env:
        :return:
        """
        service_data = self.get_all_service(env=env)
        service_list = [value.spec.ports for value in service_data.items]
        target_port = list()
        for service in service_list:
            for port in service:
                if hasattr(port, 'target_port'):
                    target_port.append(getattr(port, 'target_port'))
                if hasattr(port, 'targetPort'):
                    target_port.append(getattr(port, 'targetPort'))
        return target_port

    def get_service_ports(self, env):
        """
        :param env:
        :return:
        """
        service_data = self.get_all_service(env=env)
        service_list = [value.spec.ports for value in service_data.items]
        port_list = list()
        for service in service_list:
            for port in service:
                if hasattr(port, 'port'):
                    port_list.append(getattr(port, 'port'))
        return port_list

    def apply_deployment(self, data, namespace, env, name):
        """
        :param data:
        :param namespace:
        :param env:
        :param name:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        try:
            self.login(key_file=env_yaml)
            v1 = client.AppsV1Api()
            if self.check_deploy(namespace=namespace, env=env, deploy=name):
                v1.patch_namespaced_deployment(body=data, namespace=namespace, name=name)
            else:
                v1.create_namespaced_deployment(body=data, namespace=namespace)
            RecodeLog.info(msg="Kubernetes容器更新成功，环境：{0},命名空间：{1},服务：{2}".format(env, name, name))
            return True
        except Exception as error:
            RecodeLog.error(msg="Kubernetes容器更新成功，环境：{0},命名空间：{1},服务：{2}，原因：".format(env, name, name, error))
            return False

    def apply_service(self, data, namespace, env, name):
        """
        :param data:
        :param namespace:
        :param env:
        :param name:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        try:
            self.login(key_file=env_yaml)
            v1 = client.CoreV1Api()
            if self.check_service(service=name, namespace=namespace, env=env):
                v1.patch_namespaced_service(body=data, namespace=namespace, name=name)
            else:
                v1.create_namespaced_service(body=data, namespace=namespace)
            RecodeLog.info(msg="Kubernetes服务生成成功，环境：{0},命名空间：{1},服务：{2}".format(env, name, name))
            return True
        except Exception as error:
            RecodeLog.info(msg="Kubernetes服务生成失败，环境：{0},命名空间：{1},服务：{2}，原因：".format(env, name, name, error))
            return False

    @staticmethod
    def write_yaml(achieve, data):
        """
        :param achieve:
        :param data:
        :return:
        """
        try:
            with open(achieve, "w") as f:
                yaml.dump(data, f)
                f.close()
                RecodeLog.info(msg="执行成功, 保存内容是：{0}".format(data))
                return True
        except Exception as error:
            RecodeLog.error(msg="执行失败, 保存内容是：{0}，原因:{1}".format(data, error))
            return False

    @staticmethod
    def read_yaml(achieve):
        """
        :param achieve:
        :return:
        """
        try:
            with open(achieve, 'r') as fff:
                data = yaml.load(fff, Loader=yaml.FullLoader)
                RecodeLog.info(msg="读取文件成功:{0}".format(achieve))
                return data
        except Exception as error:
            RecodeLog.error(msg="读取文件失败:{0},原因:{1}".format(achieve, error))
            return dict()

    def check_service_node_port_in_yaml(self, port, service_name, namespace):
        """
        :param port:
        :param service_name:
        :param namespace:
        :return:
        """
        for achieve in glob.glob(os.path.join(SERVICE_YAML_DIR, "*.yaml")):
            data = self.read_yaml(achieve=achieve)
            ports = data['spec']['ports']
            service = data['metadata']['name']
            namespace_yaml = data['metadata']['namespace']
            # 判断类型为nodePort才处理
            if data['spec']['type'] not in ['NodePort', 'node_port']:
                continue
            # 当服务一致时跳过
            if namespace == namespace_yaml and service_name == service:
                continue
            node_ports = [x['nodePort'] for x in ports if 'nodePort' in ports]
            if port in node_ports:
                return True
        return False

    def docker_image_list(self):
        return self.docker_client.images.list()

    def docker_local_image_remove(self, image_name):
        self.docker_client.images.remove(image=image_name)

    def docker_image_build(self, path, tag, version):
        """
        :param path:
        :param tag:
        :param version:
        :return:
        """
        repository = "{0}:{1}".format(tag, version)
        self.docker_client.images.build(path=path, tag=repository)

    def docker_image_push(self, repository, tag=None):
        """
        :param repository:
        :param tag:
        :return:
        """
        self.docker_client.images.push(repository=repository, tag=tag)

    def split_args(self, env_args):
        """
        :param env_args:
        :return:
        """
        if not isinstance(env_args, str):
            raise TypeError("请输入字符串类型!")
        env = list()
        data = list(set(env_args.split("|")))

        for name in data:
            middleware_config = self.get_middleware_config(name=name)
            env.extend(middleware_config)
        return env

    @staticmethod
    def get_middleware_config(name):
        """
        :param name:
        :return:
        """
        if name not in MIDDLEWARE:
            RecodeLog.error(msg="{0},中间件不存在配置文件中setting.MIDDLEWARE,请检查是否填写错误，或者请添加相关中间件配置！".format(
                name
            ))
            raise KeyError("{0},中间件不存在配置文件中setting.MIDDLEWARE,请检查是否填写错误，或者请添加相关中间件配置！".format(
                name
            ))
        env = list()
        for key, value in MIDDLEWARE[name].items():
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            env.append({
                "name": key,
                "value": value
            })
        return env

    def format_config_deploy(
            self,
            namespace,
            service_name,
            image_tag,
            container_port,
            replicas,
            env_args=None
    ):
        """
        :param namespace:
        :param service_name:
        :param image_tag:
        :param container_port:
        :param replicas:
        :param env_args:
        :return:
        """
        if not env_args:
            return {
                'kind': 'Deployment',
                'spec': {
                    "replicas": int(replicas),
                    "selector": {
                        "matchLabels": {
                            "app": service_name
                        }},
                    'template': {
                        'spec': {
                            'containers': [{
                                'image': image_tag,
                                'imagePullPolicy': 'Always',
                                'ports': container_port,
                                'name': service_name
                            }]
                        }, 'metadata': {
                            'labels': {
                                'app': service_name
                            }
                        }
                    }
                },
                'apiVersion': 'apps/v1',
                'metadata': {
                    'namespace': namespace,
                    'name': service_name
                }
            }
        else:
            # 获取环境变量
            env = self.split_args(env_args=env_args)
            return {
                'kind': 'Deployment',
                'spec': {
                    "replicas": int(replicas),
                    "selector": {
                        "matchLabels": {
                            "app": service_name
                        }},
                    'template': {
                        'spec': {
                            'containers': [{
                                'image': image_tag,
                                'imagePullPolicy': 'Always',
                                'ports': container_port,
                                'env': env,
                                'name': service_name
                            }]
                        }, 'metadata': {
                            'labels': {
                                'app': service_name
                            }
                        }
                    }
                },
                'apiVersion': 'apps/v1',
                'metadata': {
                    'namespace': namespace,
                    'name': service_name
                }
            }

    @staticmethod
    def format_service(service_name, namespace, node_port_set, port_type):
        """
        :param service_name:
        :param namespace:
        :param node_port_set:
        :param port_type:
        :return:
        """
        if port_type == "ClusterIP":
            spec = {
                'ports': node_port_set,
                'selector': {'app': service_name},
                'type': 'ClusterIP'
            }
        elif port_type in ['NodePort', 'node_port']:
            spec = {
                'ports': node_port_set,
                'selector': {'app': service_name},
                'type': 'NodePort'
            }
        else:
            raise ValueError("没有获取到正确的端口类型")
        service = {
            'kind': 'Service',
            'spec': spec,
            'apiVersion': 'v1',
            'metadata': {
                'namespace': namespace,
                'name': service_name
            }
        }
        return service

    def make_node_port(self, service_name, namespace, data, start=30000, step=1):
        """
        :param service_name:
        :param namespace:
        :param data:
        :param start:
        :param step:
        :return:
        """
        if start in data:
            now = start + step
            self.make_node_port(start=now, data=data, step=step, service_name=service_name, namespace=namespace)
        elif self.check_service_node_port_in_yaml(port=start, service_name=service_name, namespace=namespace):
            now = start + step
            self.make_node_port(start=now, data=data, step=step, service_name=service_name, namespace=namespace)
        else:
            return start

    def make_service_yaml(
            self,
            namespace,
            service_name,
            port_type,
            exist_node_port,
            ports,
            env
    ):
        """
        :param namespace:
        :param service_name:
        :param port_type:
        :param exist_node_port:
        :param ports:
        :param env:
        :return:
        """
        if len(ports) == 0:
            RecodeLog.warn(msg="没有端口")
            return True
        node_ports = list()
        service_achieve = os.path.join(
            SERVICE_YAML_DIR,
            "service_{0}.yaml".format(service_name)
        )
        if os.path.exists(service_achieve):
            RecodeLog.info(
                msg="Service:{1}，服务对应的配置文件：{0}，已存在，跳过创建！".format(service_achieve, service_name)
            )
            # 读取已经存在的yaml文件
            service_yaml = self.read_yaml(achieve=service_achieve)
            # 执行已经存在的yaml文件内容
            if not self.apply_service(
                    data=service_yaml,
                    namespace=namespace,
                    env=env,
                    name=service_name
            ):
                return False
            return True
        for port in ports:
            if port_type == "NodePort":
                node_ports.append({
                    'name': "{0}-{1}".format(service_name, port),
                    'nodePort': self.make_node_port(
                        data=exist_node_port,
                        service_name=service_name,
                        namespace=namespace
                    ),
                    'port': int(port),
                    'protocol': 'TCP',
                    'targetPort': int(port)
                })
            else:
                node_ports.append({
                    'name': "{0}-{1}".format(service_name, port),
                    'port': int(port),
                    'protocol': 'TCP',
                    'targetPort': int(port)
                })
        service_yaml = self.format_service(
            namespace=namespace,
            node_port_set=node_ports,
            port_type=port_type,
            service_name=service_name
        )

        if not self.write_yaml(achieve=service_achieve, data=service_yaml):
            RecodeLog.error(msg="生成yaml文件失败：{0}".format(service_yaml))
            # raise Exception("生成yaml文件失败：{0}".format(service_yaml))
            return False
        if not self.apply_service(
                data=service_yaml,
                namespace=namespace,
                env=env,
                name=service_name
        ):
            return False
        return True

    def make_deploy_yaml(
            self,
            namespace,
            service_name,
            image_tag,
            ports,
            env,
            version,
            replicas,
            env_args
    ):
        """
        :param namespace:
        :param service_name:
        :param image_tag:
        :param ports:
        :param env:
        :param version:
        :param replicas:
        :param env_args:
        :return:
        """
        deploy_yaml = os.path.join(
            DEPLOY_YAML_DIR,
            "deploy_{0}_{1}.yaml".format(service_name, version)
        )
        if os.path.exists(deploy_yaml):
            RecodeLog.warn(msg="{0}:文件已经存在，以前可能已经部署过，请检查后再执行！".format(deploy_yaml))
            return False
        # 容器内部端口
        container_port = list()
        # container port获取
        for x in ports:
            container_port.append({
                'containerPort': int(x)
            })
        # 初始化服务的dict
        deploy_dict = self.format_config_deploy(
            namespace=namespace,
            service_name=service_name,
            image_tag="{0}:{1}".format(image_tag, version),
            container_port=container_port,
            env_args=env_args,
            replicas=replicas
        )
        # 生成yaml
        if not self.write_yaml(achieve=deploy_yaml, data=deploy_dict):
            RecodeLog.error(msg="生成yaml文件失败：{0}".format(deploy_yaml))
            return False
        if not self.apply_deployment(
                data=deploy_dict,
                namespace=namespace,
                env=env,
                name=service_name
        ):
            return False
        return True

    def format_pom_xml(self, src, dsc, deploy_name):
        """
        :param src:
        :param dsc:
        :param deploy_name:
        :return:
        """
        dom_tree = parse(src)
        root_node = dom_tree.documentElement
        for project in root_node.childNodes:
            if project.nodeName != "artifactId":
                continue
            project.childNodes[0].nodeValue = deploy_name

        with open(dsc, 'w') as f:
            dom_tree.writexml(f, addindent='  ')
        RecodeLog.info("修改pom.xml文件成功：{0}".format(dsc))

    def front_build_pre(self, path, dockerfile_path, deploy_name):
        """
        :param path:
        :param dockerfile_path:
        :param deploy_name:
        :return:
        """
        bootstrap_dict = {
            "spring": {
                "application": {
                    "name": deploy_name
                },
                "cloud": {
                    "consul": {
                        "host": "${consul_host:127.0.0.1}",
                        "port": "${consul_port:8500}",
                        "enabled": True,
                        "discovery": {
                            "enabled": True,
                            "instance-id": "${spring.application.name}:${server.port}",
                            "prefer-ip-address": True,
                            "health-check-interval": "10s",
                            "hostname": "${spring.application.name}",
                            "service-name": "${spring.application.name}"
                        }
                    }
                },
                "mvc": {
                    "favicon": {
                        "enabled": False
                    }
                },
                "boot": {
                    "admin": {
                        "client": {
                            "url": "${nccc_admin_monitor:http://localhost:9020}",
                            "instance": {
                                "prefer-ip": True
                            }
                        }
                    }
                }
            },
            "server": {
                "port": "${server-port:8888}"
            }
        }
        if not os.path.exists(dockerfile_path):
            RecodeLog.error(msg="前端编译依赖的目录不存在，请检查")
            raise Exception("前端编译依赖的目录不存在，请检查")
        if os.path.exists(path):
            RecodeLog.warn(msg="存在之前的目录:{0},删除！".format(path))
            shutil.rmtree(path=path)
        shutil.copytree(src=dockerfile_path, dst=path)
        # 写入文件bootstrap
        bootstrap_yaml = os.path.join(path, 'target', 'classes', 'bootstrap.yml')
        if not self.write_yaml(achieve=bootstrap_yaml, data=bootstrap_dict):
            raise Exception("写入文件失败:{0},内容:{1}".format(bootstrap_yaml, bootstrap_dict))
        self.format_pom_xml(src=SRC_POM_DIR, dsc=os.path.join(path, 'pom.xml'), deploy_name=deploy_name)

    def complete(
            self,
            env,
            namespace,
            service,
            version,
            port_type,
            env_args,
            replicas=1
    ):
        """
        :param env:
        :param namespace:
        :param service:
        :param version:
        :param port_type:
        :param env_args:
        :param replicas:
        :return:
        """
        # 编译程序所在目录
        service_path = os.path.join(WORKSPACE, service)
        # 镜像标签
        tag = os.path.join(HARBOR_URL, service)
        # 获取到的容器内部存在的node_port
        node_port = self.get_service_nodeports(env=env)
        # ##############镜像相关的操作#####################
        front_app = os.path.join(service_path, 'package.json')
        backend_app = os.path.join(service_path, 'pom.xml')
        # front_docker_path = os.path.join(service_path, 'docker')
        if os.path.exists(front_app) and os.path.exists(backend_app):
            RecodeLog.error(msg="{2}.同时出现前端和后端的配置：{0},{1}".format(
                front_app, backend_app, service
            ))
            return False
        elif os.path.exists(front_app):
            RecodeLog.info(msg="{0},应用为前端应用,开始编译....".format(service))
            exec_npm_str = "cd {0} && yarn".format(service_path)
            if env in ['qa', 'dev']:
                exec_npm_run_str = "cd {0} && yarn build:{1}".format(service_path, env)
            else:
                exec_npm_run_str = "cd {0} && yarn build".format(service_path, env)
            try:
                self.exec_command(command=exec_npm_str)
                RecodeLog.info("执行编译成功：{0}".format(exec_npm_str))
                self.exec_command(command=exec_npm_run_str)
                RecodeLog.info("执行编译成功：{0}".format(exec_npm_run_str))
                self.docker_image_build(path=service_path, tag=tag, version=version)
                RecodeLog.info(msg="生成前端镜像成功:{0}:{1}".format(tag, version))
                self.docker_image_push(repository="{0}:{1}".format(tag, version))
                RecodeLog.info(msg="推送前端镜像成功:{0}:{1}".format(tag, version))
                self.docker_local_image_remove(image_name="{0}:{1}".format(tag, version))
                RecodeLog.info(msg="删除镜像成功：{0}:{1}".format(tag, version))
            except Exception as error:
                RecodeLog.error("执行编译异常，原因：{0}".format(error))
                return False
        elif env in ['dev'] and os.path.exists(backend_app):

            try:
                self.docker_image_build(path=service_path, tag=tag, version=version)
                RecodeLog.info(msg="生成后端镜像成功:{0}:{1}".format(tag, version))
                self.docker_image_push(repository="{0}:{1}".format(tag, version))
                RecodeLog.info(msg="推送后端镜像成功:{0}:{1}".format(tag, version))
                self.docker_local_image_remove(image_name="{0}:{1}".format(tag, version))
                RecodeLog.info(msg="删除镜像成功：{0}:{1}".format(tag, version))
            except Exception as error:
                RecodeLog.error("执行编译异常，原因：{0}".format(error))
                return False

        ports = self.get_port(path=service_path)
        if not self.make_service_yaml(
                namespace=namespace,
                service_name=service,
                port_type=port_type,
                ports=ports,
                exist_node_port=node_port,
                env=env
        ):
            return False

        if not self.make_deploy_yaml(
                namespace=namespace,
                service_name=service,
                image_tag=tag,
                ports=ports,
                env=env,
                env_args=env_args,
                version=version,
                replicas=replicas
        ):
            return False
        return True

    @staticmethod
    def show_middleware():
        for key, value in MIDDLEWARE.items():
            print("+++++++++++++++++++++++++++++++")
            print("中间件：{0},包括以下变量:".format(key))
            for k, v in value.items():
                print("{0}={1}".format(k, v))
            print("-------------------------------")

    @staticmethod
    def get_port(path, rex='EXPOSE'):
        """
        :param rex:
        :param path:
        :return:
        """
        docker_file = os.path.join(path, 'Dockerfile')
        if not os.path.exists(docker_file):
            RecodeLog.warn(msg="不存在{0},可能为前端服务，请确认！".format(docker_file))
            return []

        with open(docker_file, 'r') as fff:
            data = fff.readlines()
        port = list()
        for line in data:
            if rex in line:
                port.append(line.split(" ")[1].replace('\n', '').replace(' ', ''))
            else:
                continue
        return port

    @staticmethod
    def send_alert(content):
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "isAtAll": False
            }
        }

        headers = {'Content-Type': 'application/json'}
        timestamps = long(round(time.time() * 1000))
        url = "https://oapi.dingtalk.com/robot/send?access_token={0}".format(
            DINGDING_TOKEN)  # 说明：这里改为自己创建的机器人的webhook的值
        secret_enc = bytes(DINGDING_SECRET).encode('utf-8')
        to_sign = '{}\n{}'.format(timestamps, DINGDING_SECRET)
        to_sign_enc = bytes(to_sign).encode('utf-8')
        hmac_code = hmac.new(secret_enc, to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.quote_plus(base64.b64encode(hmac_code))
        url = "{0}&timestamp={1}&sign={2}".format(url, timestamps, sign)
        try:
            x = requests.post(url=url, data=json.dumps(data), headers=headers)
            if x.json()["errcode"] != 0:
                raise Exception(x.content)
            RecodeLog.info(msg="发送报警成功,url:{0},报警内容:{1}".format(url, data))
        except Exception as error:
            RecodeLog.info(msg="发送报警失败,url:{0},报警内容:{1},原因:{2}".format(url, data, error))
