import requests

class pypilib:
    def __init__(self):
        self.simple_url = "https://pypi.org/simple/" # contains a cached list of every project on pypi.org

    def get_simple(self):
        pypi_projects = []
        
        response = self.request_get(self.simple_url)

        pypi_urls =  response.text.split("\n")
        for url in pypi_urls:
            if 'href' in url:
                parts = url.split('">')
                project_name = parts[1][:-4]
                project_url = f"https://pypi.org/project/{project_name}/"

                data = {'name': project_name, 'url': project_url}
                pypi_projects.append(data)

        return pypi_projects

    def request_get(self, url):
        response =  requests.get(url)

        return response