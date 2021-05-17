import requests

class external_server:
    def __init__(self, external, jar):
        self.external = external
        self.jar = jar
        self.start_connection()

    
    def getMELI(self, MELI):
        requests.get("https://wms.mercadolibre.com.ar/api/reports/skus/export/INVENTORIES?inventory_id={}&fields=inventory_id%2Cwidth_value%2Clength_value%2Cheight_value".format(dire), cookies=jar).text