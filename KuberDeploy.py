# -*- coding: utf-8 -*-
import getopt
import sys
from lib.PyKuber import PyKuber
from collections import Counter


def useage():
    print("%s -h\t#帮助文档" % sys.argv[0])
    print(
            "%s -n 命名空间 -s服务名称 -e 所属环境 -v版本号 -t[NodePort|ClusterIP](端口类型) -r副本个数 -a'变量名1|变量名2'\t#部署对应环境代码" %
            sys.argv[0]
    )
    print("%s -m #查看可支持的中间件列表" % sys.argv[0])


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "n:s:e:ht:v:a:mr:"
        )
    except getopt.GetoptError:
        print("%s -h" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    d = PyKuber()
    # 帮助
    command_dict_1 = ['-s', '-n', '-e', '-v', '-t']
    command_dict_2 = ['-s', '-n', '-e', '-v', '-t', '-a']
    command_dict_3 = ['-s', '-n', '-e', '-v', '-t', '-r']
    command_dict_4 = ['-s', '-n', '-e', '-v', '-t', '-r', '-a']
    if ["-h"] == command_dict.keys():
        useage()
        sys.exit()
    # 获取监控项数据

    elif Counter(command_dict.keys()) == Counter(command_dict_1) or \
            Counter(command_dict.keys()) == Counter(command_dict_2) or \
            Counter(command_dict.keys()) == Counter(command_dict_3) or \
            Counter(command_dict.keys()) == Counter(command_dict_4):
        command_data = dict()
        command_data['service'] = command_dict.get('-s')
        command_data['namespace'] = command_dict.get("-n")
        command_data['env'] = command_dict.get('-e')
        command_data['version'] = command_dict.get("-v")
        command_data['port_type'] = command_dict.get("-t")
        # 判断端口类型
        if command_data['port_type'] not in ['ClusterIP', 'NodePort']:
            raise Exception("获取类型错误")
        if '-a' in command_dict:
            command_data['env_args'] = command_dict.get("-a")
        if '-r' in command_dict:
            command_data['replicas'] = command_dict.get("-r")
        if d.complete(**command_data):
            dingding_str = "更新提示：\n\t更新环境:{0}\n\t命名空间:{1}\n\t服务:{2}\n\t版本号:{3}\n\t状态:更新成功".format(
                command_data['env'],
                command_data['namespace'],
                command_data['service'],
                command_data['version']
            )
        else:
            dingding_str = "更新提示：\n\t更新环境:{0}\n\t命名空间:{1}\n\t服务:{2}\n\t版本号:{3}\n\t状态:更新失败".format(
                command_data['env'],
                command_data['namespace'],
                command_data['service'],
                command_data['version']
            )
        d.send_alert(content=dingding_str)
    elif ["-m"] == command_dict.keys():
        d.show_middleware()
    else:
        useage()
        sys.exit(1)


if __name__ == "__main__":
    main()
