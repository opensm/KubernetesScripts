# -*- coding: utf-8 -*-
import os

# Kubernetes 配置
HARBOR_URL = "harbor.nccc.site/nccc/"
WORKSPACE = "/var/lib/jenkins/workspace/"
DEPLOY_YAML_DIR = "/data/yaml/deploy"
SERVICE_YAML_DIR = "/data/yaml/service"
KEY_DIR = "/data/kube"

SRC_POM_DIR = os.path.join(os.path.dirname(__file__), 'pom.xml')
# 日志配置
LOG_DIR = "/tmp"
LOG_FILE = "python_deploy.log"
LOG_LEVEL = "INFO"
# 钉钉告警配置
DINGDING_TOKEN = ""
DINGDING_SECRET = ""
# 中间件列表
MIDDLEWARE = {
    "rest_file": {
        "rest.file.time_out": "180000",
        "rest.file.max_size": "524288000"
    },
    "zk": {
        "regCenter_serverlist": "zk-hs.middleware"
    },
    "consul": {
        "consul_host": "consul-consul-dns.middleware",
        "consul_port": "8500"
    },
    "redis_database": {
        "redis_host": "redis.nccc-dev",
        "redis_port": "6379",
        "redis_database": "1"
    },
    "redis_database_4": {
        "redis_host": "redis.nccc-dev",
        "redis_port": "6379",
        "redis_database": "4"
    },
    "redis": {
        "redis_host": "redis.nccc-dev",
        "redis_port": "6379"
    },
    'redis_address': {
        "redis_address": "redis.nccc-dev:6379"
    },
    "pgsql_attendant": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/attendant",
        "pgsql_username": "postgres"
    },
    "pgsql_quality": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/quality",
        "pgsql_username": "postgres"
    },
    "pgsql_zhanwu": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/zhanwu",
        "pgsql_username": "postgres"
    },
    "pgsql_toilet": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/toilet",
        "pgsql_username": "postgres"
    },
    "pgsql_basicinfo": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/basicinfo",
        "pgsql_username": "postgres"
    },
    "pgsql_messagecenter": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/messagecenter",
        "pgsql_username": "postgres"
    },
    "pgsql_refcard": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/refcard",
        "pgsql_username": "postgres"
    },
    "pgsql_elasticjob": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/elasticjob",
        "pgsql_username": "postgres"
    },
    "pgsql_trainplan": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/trainplan",
        "pgsql_username": "postgres"
    },
    "pgsql_log": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/log",
        "pgsql_username": "postgres"
    },
    "pgsql_workflow": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/workflow",
        "pgsql_username": "postgres"
    },
    "pgsql_onlinelearn": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/onlinelearn",
        "pgsql_username": "postgres"
    },
    "pgsql_auth": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/auth",
        "pgsql_username": "postgres"
    },
    "pgsql_uc": {
        "pgsql_password_uc": "postgres",
        "pgsql_url_uc": "jdbc:postgresql://10.253.100.71:5432/auth",
        "pgsql_username_uc": "postgres"
    },
    "pgsql_opinioncenter": {
        "pgsql_password_uc": "postgres",
        "pgsql_url_uc": "jdbc:postgresql://10.253.100.71:5432/opinioncenter",
        "pgsql_username_uc": "postgres"
    },
    "pgsql_passengerflowwarning": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/passengerflowwarning",
        "pgsql_username": "postgres"
    },
    "pgsql": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/postgres",
        "pgsql_username": "postgres"
    },
    "pgsql_ticket": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/ticket",
        "pgsql_username": "postgres"
    },
    "pgsql_cddt": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/cddt",
        "pgsql_username": "postgres"
    },
    "pgsql_supervisor": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/supervisor",
        "pgsql_username": "postgres"
    },
    "pgsql_external_auth": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.71:5432/external_auth",
        "pgsql_username": "postgres"
    },
    "pgsql_t": {
        "pgsql_password_t": "ncccdqpg",
        "pgsql_url_t": "jdbc:postgresql://10.253.100.39:5432/postgres",
        "pgsql_username_t": "postgres"
    },
    "pgsql_o": {
        "pgsql_password_o": "postgres",
        "pgsql_url_o": "jdbc:postgresql://10.253.100.9:5432/postgres",
        "pgsql_username_o": "postgres"
    },
    "pgsql_i": {
        "pgsql_password_i": "postgres",
        "pgsql_url_i": "jdbc:postgresql://10.253.100.9:5432/postgres",
        "pgsql_username_i": "postgres"
    },
    "pgsql_b": {
        "pgsql_password_b": "postgres",
        "pgsql_url_b": "jdbc:postgresql://10.253.100.8:5432/nois_basicdata",
        "pgsql_username_b": "postgres"
    },
    "pgsql_dqkl": {
        "pgsql_password": "postgres",
        "pgsql_url": "jdbc:postgresql://10.253.100.9:5432/postgres",
        "pgsql_username": "postgres"
    },
    "pgsql_39": {
        "pgsql_password": "ncccdqpg",
        "pgsql_url": "jdbc:postgresql://10.253.100.39:5432/postgres",
        "pgsql_username": "postgres"
    },
    "zipkin": {
        "zipkin_url": "http://zipkin.middleware:9411"
    },
    "admin_monitor": {
        "nccc_admin_monitor": "http://nccc-admin-monitor.nccc-monitor:9020"
    },
    "spring": {
        "spring.profiles.active": "dev"
    },
    "kafka": {
        "kafka_address": "kafka-svc.middleware:9092"
    },
    "mail": {
        "mail.username": "1098588843@qq.com",
        "mail.password": "lf87289610",
        "mail.host": "smtp.qq.com",
        "mail.port": 25
    },
    "wechat": {
        "rest.wechat.wechat_api": "https://qyapi.weixin.qq.com/cgi-bin/",
        "rest.wechat.s_token": "XBJry8YNWMHjpIsL9d",
        "rest.wechat.s_encodingAESKey": "hcLQHQ5UIPU23iobVL3oC7Dvi8anmKne3WHpdCocQCW",
        "rest.wechat.enterprise_id": "ww29abdbc4cdba6695",
        "rest.wechat.app_secret": "cBpn0j9DWLVua62mk5cZM0msEoiHRePFneB0rN9hXsg",
        "rest.wechat.agent_id": 1000002
    },
    'wechat_1': {
        'rest.wechat.wechat_api': "https://qyapi.weixin.qq.com/cgi-bin/",
        'rest.wechat.apptokenkey.app_info': 'access_token_for_login'
    },
    "sync_corn": {
        "sync_corn": "0 */5 * * * ?"
    },
    "mail_port": {
        "mail.port": 25
    },
    "app_url": {
        "app_url": "https://cdmetrotest.cnzhiyuanhui.com"
    },
    "news_url": {
        "news_url": "http://10.253.100.32:12315"
    },
    "opinion": {
        "opinion_url": "http://cddt.gstai.com/webapi",
        "opinion_msgTemplate": "【NCCC舆情预警开发】您好！接受到一条舆情预警信息，点击链接查看详情，请尽快处理！http://10.253.100.11:31896?code=%s。",
        "opinion_email_subject": "【NCCC舆情预警(开发)】"
    },
    "rest_url": {
        "rest.url.weather": "https://cdmetro.cnzhiyuanhui.com/op/weather/",
        "rest.url.stationFacility": "https://cdmetro.cnzhiyuanhui.com/op/stations/",
        "rest.url.lastTrainLimit": "https://wework-api.cdmetrokyb.com/metro_network_calculation/core/"
    }
}
