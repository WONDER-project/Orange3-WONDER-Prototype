from Orange.canvas.application.addons import PipInstaller

class Package:
    def __init__(self, package_url):
        self.package_url = package_url

if __name__ == '__main__':
    pip = PipInstaller()
    print(pip.arguments)
