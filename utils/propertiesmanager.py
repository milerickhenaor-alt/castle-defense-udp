import os

class PropertiesManager:

    def __init__(self, path="assets/config.properties"):
        self.properties = {}

        # 🔥 Mostrar ruta real (debug útil)
        full_path = os.path.abspath(path)
        print("Cargando config desde:", full_path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró el archivo: {full_path}")

        with open(path, "r") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                self.properties[key.strip()] = value.strip()

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def get_int(self, key, default=0):
        try:
            return int(self.get(key, default))
        except:
            return default