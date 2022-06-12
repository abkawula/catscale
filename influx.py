from influxdb import InfluxDBClient

class INFLUX:
    def __init__(self, host, port, db):
        self.client = InfluxDBClient(host=host, port=port)
        self.client.switch_database(db)

    def write_points(self, datapoints):
        self.client.write_points(datapoints)

    def test():
        print("This is a test")
