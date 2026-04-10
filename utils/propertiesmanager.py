class PropertiesManager:

    def __init__(self, path="assets/config.properties"):
        self.properties = {}

        with open(path, "r") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                key, value = line.split("=")
                self.properties[key.strip()] = value.strip()

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def get_int(self, key, default=0):
        return int(self.get(key, default))