import jenkins


class CopyJenkins:
    def __init__(self):
        self.jenkins = jenkins.Jenkins("http://111.111.111.111:8080/", username='admin', password='1q2w3e4r')
        self.jenkins_new = jenkins.Jenkins("http://111.111.111.112:8080/", username='admin', password='xxx@2019')

    def copy_jenkins(self):
        """
        :return:
        """
        for name in [
            'xxx', 'xxxy'
        ]:
            result = self.jenkins.get_job_config(name=name)
            self.jenkins_new.create_job(name=name, config_xml=result)


c = CopyJenkins()
c.copy_jenkins()
