import click
import boto3
import json
from io import StringIO, BytesIO
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions, ASYNCHRONOUS
filter = ["AE", "AI1", "AI2", "AI3", "API1", "API2", "API3", "API", "CE", "IE", "IPI1", "IPI2", "IPI3", "PFI1", "PFI2", "PFI3", "VAI", "VI1", "VI2", "VI3"]

#s3_paginator = boto3.client('s3').get_paginator('list_objects_v2')


idb_bucket = "energydata"
org = "circutor"
token = "k3TMVP_NnTnMH-NTEwNehH8CzYkzPoshZNUqPQ1SLM8PxA8e-SePmItW-d_wIadXtCNNgMG-weAWOIYlBZNUzw=="
# Store the URL of your InfluxDB instance
url="http://localhost:8086"


def keys(bucket_name, prefix='/', delimiter='/'):
    prefix = prefix[1:] if prefix.startswith(delimiter) else prefix
    bucket = boto3.resource('s3').Bucket(bucket_name)
    return (_.key for _ in bucket.objects.filter(Prefix=prefix))

def frombucket(s3bucket, prefix, devicesfile, client, write_api):
    s3 = boto3.client('s3')
    files = keys(s3bucket, prefix)

    total = 0
    for item in files:
        print(item)
        buf = BytesIO()
        s3.download_fileobj(s3bucket, item, buf)
        json_object = json.loads(buf.getvalue().decode("utf-8"))

        device_id = json_object["device_id"]
        if devicesfile:
            with open(devicesfile, 'r') as filedevices:
                for line in filedevices:
                    device = line.replace('\n', '')
                    print(device.rstrip())
                    if device == device_id:

                        p = influxdb_client.Point("energy")
                        for tag, value in json_object['tags'].items():
                            p.tag(tag, value)

                        for var, value in json_object['values'].items():
                            p.field(var, value)
                            p.time(json_object['ts'])
                            write_api.write(bucket=idb_bucket, org=org, record=p)

        total = total + 1
    print(total)

def fromfile(filename, devicesfile, client, write_api):
    if filename:
        with open(filename, 'r') as f:
            if filename:
                with open(filename, 'r') as f:
                    json_object = json.loads(f.read())
                    device_id = json_object["device_id"]
                    tags = json_object["tags"]
                    if devicesfile:
                        with open(devicesfile, 'r') as filedevices:
                            for line in filedevices:
                                device = line.replace('\n', '')
                                if device == device_id:
                                    p = influxdb_client.Point("energy")
                                    for tag, value in json_object['tags'].items():
                                        p.tag(tag, value)

                                    for var, value in json_object['values'].items():
                                        p.field(var, value)
                                        p.time(json_object['ts'])
                                        write_api.write(bucket=idb_bucket, org=org, record=p)


@click.command()
@click.option('--s3bucket', help='S3 to get data from')
@click.option('--prefix', default="", help='S3 prefix')
@click.option('--filename', default=None)
@click.option('--devicesfile', default=None)
@click.option('--url', default="http://localhost:8086")
def run(s3bucket, prefix, filename, devicesfile, url):


    client = influxdb_client.InfluxDBClient(
       url=url,
#       token=token,
#       org=org
    )

    write_api = client.write_api(write_options=ASYNCHRONOUS)

    if prefix and s3bucket and devicesfile:
        frombucket(s3bucket, prefix, devicesfile, client, write_api)

    if filename and devicesfile:
        fromfile(filename, devicesfile, client, write_api)




if __name__ == "__main__":
    run()
