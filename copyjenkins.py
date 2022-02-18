import jenkins


class CopyJenkins:
    def __init__(self):
        self.jenkins = jenkins.Jenkins("http://127.0.0.1:8080/", username='admin', password='111?')
        self.jenkins_new = jenkins.Jenkins("http://127.0.0.1:8080/", username='admin', password='111?')

    def copy_jenkins(self):
        """
        :return:
        """
        data = self.jenkins.get_jobs(view_name='统一车联网平台-开发')
        for task in data:
            result = self.jenkins.get_job_config(name=task['name'])
            print(result.replace(
                    'env.sh',
                    'env_test.sh'
                ))

            self.jenkins_new.create_job(
                name="{}-test".format(task['name']),
                config_xml=result.replace(
                    'env.sh',
                    'env_test.sh'
                )
            )


c = CopyJenkins()
c.copy_jenkins()
