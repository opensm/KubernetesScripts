# -*- coding: utf-8 -*-
from kubernetes import config, client
import docker
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

reload(sys)

sys.setdefaultencoding('utf-8')

LOG_DIR = "/tmp"
LOG_FILE = "python_deploy.log"
LOG_LEVEL = "INFO"

log_level = getattr(logging, LOG_LEVEL)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, 750)
RecodeLog = logging.getLogger("LOG INFO")
RecodeLog.setLevel(log_level)
# 建立一个filehandler来把日志记录在文件里，级别为debug以上
# 按天分割日志,保留30天
if not RecodeLog.handlers:
    fh = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE), when='D', interval=1, backupCount=30
    )
    ch = logging.StreamHandler()
    fh.setLevel(log_level)
    ch.setLevel(log_level)
    # 设置日志格式
    if LOG_LEVEL == "DEBUG":
        formatter = logging.Formatter(
            "%(asctime)s - Message of File(文件): %(filename)s,Module(类):%(module)s,FuncName(函数):%(funcName)s ,LineNo(行数):%(lineno)d - %(levelname)s - %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # 将相应的handler添加在logger对象中
    RecodeLog.addHandler(fh)
    RecodeLog.addHandler(ch)
HARBOR_URL = "harbor.nccc.site/nccc/"
WORKSPACE = "/var/lib/jenkins/workspace/"
YAML_DIR = "/data/kuberctl"
KEY_DIR = "/data/kube"


class PyKuber:
    def __init__(self):
        self.docker_client = docker.client.from_env()

    def login(self, key_file=os.path.join(KEY_DIR, 'config.yaml')):
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

    def get_deploys_by_namespace(self, namespace, env):
        """
        :param namespace:
        :param env:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1 = client.AppsV1Api()
        v1c = client.CoreV1Api()
        service_data = v1.list_namespaced_deployment(namespace=namespace)
        for value in service_data.items:
            v1c.list_namespaced_service(namespace=namespace)
            print("+++++++++++++++++++++++++++++++++++++++++")
            print("服务名称：{0}".format(value.metadata.name))
            if not value.spec.template.spec.containers[0].env:
                print("没有环境变量")
            else:
                env_str = ""
                for v in value.spec.template.spec.containers[0].env:
                    if 'consul' in v.name and 'host' in v.name:
                        env_str = "{0}={1},{2}".format(v.name, "consul-consul-server.nccc-dev", env_str)
                    else:
                        env_str = "{0}={1},{2}".format(v.name, v.value, env_str)
                print("变量列表:{0}".format(env_str))
            print("------------------------------------------")

    def get_namespace(self, env):
        """
        :param env:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1 = client.CoreV1Api()
        service_data = v1.list_namespace()
        for value in service_data.items:
            # print(value.metadata.name)
            self.get_deploys_by_namespace(namespace=value.metadata.name, env=env)


p = PyKuber()
p.get_namespace(env='dev')
