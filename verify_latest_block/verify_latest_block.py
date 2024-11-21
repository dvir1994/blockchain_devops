import subprocess
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

LOG_LEVEL = logging.INFO
MAX_WORKERS = 10
RPC_CALLS_TIMEOUT = 2
OUTPUT_FILE = "/tmp/endpoints.txt"

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

ws_endpoints = [
    "ws://x.x.x.x:8546",
    "wss://blast.gasswap.org",
]

http_endpoints = [
    "http://x.x.x.x:8547",
    "https://rpc.envelop.is/blast",
]


def check_ws_endpoint(endpoint):
    command = f'timeout {RPC_CALLS_TIMEOUT} wscat -x \'{{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}}\' -c {endpoint}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    try:
        result_json = json.loads(result.stdout)
        block_number = result_json.get("result")
        block_number_int_16 = int(block_number, 16)
        return f"{block_number_int_16} {endpoint}"
    except Exception as e:
        logger.debug(f"found issue with: {endpoint} - {e}")
        return None


def check_http_endpoint(endpoint):
    command = f'curl -X POST --max-time {RPC_CALLS_TIMEOUT} --data \'{{"jsonrpc":"2.0","id" :1,"method" :"eth_blockNumber","params" :[]}}\' -H \'content-type:application/json\' {endpoint}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    try:
        result_json = json.loads(result.stdout)
        block_number = result_json.get("result")
        block_number_int_16 = int(block_number, 16)
        return f"{block_number_int_16} {endpoint}"

    except Exception as e:
        logger.debug(f"found issue with: {endpoint} - {e}")
        return None


def main():
    valid_endpoints = []  # dict of tuples, with (block_number, endpoint)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(check_ws_endpoint, endpoint) for endpoint in ws_endpoints
        ]
        futures += [
            executor.submit(check_http_endpoint, endpoint)
            for endpoint in http_endpoints
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_endpoints.append(result)

        # print the valid endpoints, sorted by block number
        # write the results to a file /tmp/endpoints.txt
        with open(OUTPUT_FILE, "w") as f:
            for endpoint in sorted(
                valid_endpoints, key=lambda x: x.split()[0], reverse=True
            ):
                f.write(endpoint + "\n")
                print(endpoint)


if __name__ == "__main__":
    main()
