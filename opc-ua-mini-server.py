import sys
import time
from typing import List, Any
import asyncio
import random
from opcua import ua, Server

sys.path.insert(0, "..")


async def fetch(v_sensor):
    value = random.random()
    rtn = await loop.run_in_executor(None, v_sensor.set_value, value)           # run in executor 사용
    if rtn:
        return len(rtn)
    else:
        return 0


async def a_main():
    futures = [asyncio.ensure_future(fetch(sens)) for sens in sensors]
    result = await asyncio.gather(*futures)                # 결과를 한꺼번에 가져옴
    # print(result)


if __name__ == "__main__":

    # sensor list
    with open("sensor.txt", "r") as f:
        sensor_metrics = f.read().splitlines()
        # sensor_metrics = f.readlines().strip('\n')

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4847/hrc_poc/")

    # setup our own namespace, not really necessary but should as spec
    uri = "hrc_poc"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # populating our address space
    myobj = objects.add_object(idx, "MyObject")

    # iter
    myvar = myobj.add_variable(idx, "0_Variable", 0.7)
    myvar.set_writable()  # Set MyVariable to be writable by clients

    # sensor iter
    sensors = [myobj.add_variable(idx, item, 0.0) for item in sensor_metrics]
    for sensor in sensors:
        sensor.set_writable()

    loop = asyncio.get_event_loop()  # 이벤트 루프를 얻음
    # starting!
    server.start()

    try:
        count = 0
        while True:
            time.sleep(1)
            count += 0.1

            # iter
            myvar.set_value(count)

            # async set value
            loop.run_until_complete(a_main())  # main이 끝날 때까지 기다림

    finally:
        # close connection, remove subcsriptions, etc
        server.stop()
        loop.close()
