# -*- coding: utf-8 -*-
import sys
import getopt
import simplejson as json
import yaml
from kubernetes import config, client
import docker
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import xmltodict
import commands
import re
import jenkins
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
        self.jenkins = jenkins.Jenkins("http://111.111.111.111:8080/", username='admin', password='admin')

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

    def get_service_by_deploy(self, namespace, env, service_name):
        """
        :param namespace:
        :param env:
        :param service_name:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1c = client.CoreV1Api()
        service = v1c.list_namespaced_service(namespace=namespace)
        port_args = ""
        port_type = ""
        for v in service.items:
            if service_name != v.metadata.name:
                continue
            for value in v.spec.ports:
                port_arg = ""
                port_arg = "{0}={1},{2}".format('port', getattr(value, 'port'), port_arg)
                if hasattr(value, 'node_port'):
                    port_arg = "{0}={1},{2}".format('nodePort', getattr(value, 'node_port'), port_arg)
                if hasattr(value, 'NodePort'):
                    port_arg = "{0}={1},{2}".format('nodePort', getattr(value, 'node_port'), port_arg)
                if hasattr(value, 'targetPort'):
                    port_arg = "{0}={1},{2}".format('targetPort', getattr(value, 'targetPort'), port_arg)
                if hasattr(value, 'target_port'):
                    port_arg = "{0}={1},{2}".format('targetPort', getattr(value, 'target_port'), port_arg)
                if hasattr(value, 'name'):
                    port_arg = "{0}={1},{2}".format('name', getattr(value, 'name'), port_arg)
                port_arg = port_arg.rstrip(',')
                port_args = "{0}|{1}".format(port_arg, port_args)
            port_type = v.spec.type
        return {
            "PortType": port_type,
            "PortStr": port_args.rstrip('|')
        }

    def get_deploys_by_namespace(self, namespace, env):
        """
        :param namespace:
        :param env:
        :return:
        """
        env_yaml = os.path.join(KEY_DIR, "{0}.yaml".format(env))
        self.login(key_file=env_yaml)
        v1 = client.AppsV1Api()
        service_data = v1.list_namespaced_deployment(namespace=namespace)
        for value in service_data.items:
            port_args = self.get_service_by_deploy(namespace=namespace, env=env, service_name=value.metadata.name)
            if not port_args['PortType'] or not port_args['PortStr']:
                RecodeLog.warning(msg="没有获取到:{0}".format(value.metadata.name))
                continue
            RecodeLog.info(msg="开始处理服务：{0}，相关的环境变量".format(value.metadata.name))
            if not value.spec.template.spec.containers[0].env:
                exec_str = '''sudo /usr/bin/pythonvir /oper/deploy/KuberDeploy.py -n %s -s %s -e %s -t %s -v v${BUILD_NUMBER}''' % (
                    namespace, value.metadata.name, env, port_args['PortType']
                )
            else:
                env_str = ""
                for v in value.spec.template.spec.containers[0].env:
                    if 'consul' in v.name and 'consul' not in env_str:
                        env_str = "{0}|{1}".format("consul", env_str)
                    elif 'consul' in v.name and 'consul' in env_str:
                        continue
                    elif 'redis' in v.name and 'redis' not in env_str:
                        env_str = "{0}|{1}".format("redis", env_str)
                    elif 'redis' in v.name and 'redis' in env_str:
                        continue
                    elif 'kafka' in v.name and 'kafka' not in env_str:
                        env_str = "{0}|{1}".format("kafka", env_str)
                    elif 'kafka' in v.name and 'kafka' in env_str:
                        continue
                    elif 'zipkin' in v.name and 'zipkin' not in env_str:
                        env_str = "{0}|{1}".format("zipkin", env_str)
                    elif 'zipkin' in v.name and 'zipkin' in env_str:
                        continue
                    elif 'spring' in v.name and 'spring' not in env_str:
                        env_str = "{0}|{1}".format("spring", env_str)
                    elif 'spring' in v.name and 'spring' in env_str:
                        continue
                    elif 'pgsql' in v.name and 'pgsql' not in env_str:
                        env_str = "{0}|{1}".format("pgsql", env_str)
                    elif 'pgsql' in v.name and 'pgsql' in env_str:
                        continue
                    elif 'admin_monitor' in v.name and 'admin_monitor' not in env_str:
                        env_str = "{0}|{1}".format("admin_monitor", env_str)
                    elif 'admin_monitor' in v.name and 'admin_monitor' in env_str:
                        continue
                    else:
                        RecodeLog.warning(msg="不存在的变量:{0}".format(v))
                exec_str = '''sudo /usr/bin/pythonvir /oper/deploy/KuberDeploy.py -n %s -s %s -e %s -a "%s" -t %s -v v${BUILD_NUMBER}''' % (
                    namespace,
                    value.metadata.name,
                    env,
                    env_str.rstrip('|'),
                    port_args['PortType']
                )
            RecodeLog.info(msg="完成处理服务：{0}，相关的环境变量".format(value.metadata.name))
            try:
                result = self.jenkins.get_job_config(name=value.metadata.name)
                pattern = re.compile(r'(<command>)(.*)(</command>)')
                command_config = pattern.sub(r'<command>{0}</command>'.format(exec_str), result)
                pattern_key = re.compile(r'(<credentialsId>)(.*)(</credentialsId>)')
                result_config = pattern_key.sub(
                    r'<credentialsId>f85b80ba-7402-4b83-951a-4078d5f6a754</credentialsId>',
                    command_config
                )
                self.jenkins.reconfig_job(name=value.metadata.name, config_xml=result_config)
                RecodeLog.info(msg="修改成功：{0}".format(value.metadata.name))
                # self.jenkins.build_job(name=value.metadata.name)
                # RecodeLog.info(msg="构建发送成功：{0}".format(value.metadata.name))
            except Exception as error:
                RecodeLog.error(msg="修改失败：{0},{1}".format(value.metadata.name, error))
                continue

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
