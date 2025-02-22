class Repository():
    url: str
    name: str
    is_industry_backed: bool

    def __init__(self, url, name, is_industry_backed):
        self.url = url
        self.name = name
        self.is_industry_backed = is_industry_backed

repositories = []

repositories.append(Repository("microsoft/vscode", "VSCode", 1))
repositories.append(Repository("facebook/react", "React", 1))
repositories.append(Repository("kubernetes/kubernetes", "Kubernetes", 1))
repositories.append(Repository("golang/go", "Golang", 1))
repositories.append(Repository("angular/angular", "Angluar", 1))
repositories.append(Repository("pytorch/pytorch", "Pytorch", 1))
repositories.append(Repository("ansible/ansible", "Ansibile", 1))

repositories.append(Repository("godotengine/godot", "Godo", 0))
repositories.append(Repository("obsproject/obs-studio", "OBS-Studio", 0))
repositories.append(Repository("mattermost/mattermost-server", "Mattermost-server", 0))
repositories.append(Repository("openstreetmap/openstreetmap-website", "Open Street Map", 0))
#repositories.append(Repository("KDE/krita", "Krita", 0))
repositories.append(Repository("discourse/discourse", "Discourse", 0))
repositories.append(Repository("jenkinsci/jenkins", "Jenkins", 0))