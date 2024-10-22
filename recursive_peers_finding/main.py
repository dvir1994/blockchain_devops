# 1. iterate over input file with IPs
# 2. for each IP check WS and RPC - see if they reply to expected eth_chainId - and save to a set
# 3. recursivley go over all endpoints in the set, and get all of their peers
# 4. now for each acquired peer, check if they reply to expected eth_chainId - and save to a set
# 5. for each saved IP of RPC and WS in the sets, check the blockNumber
# 6. save to CSV output file all WS and FTM nodes with the eth_blockNumber of each (ip, ws/rpc, blockNumber)


import csv
import json
import asyncio
import subprocess
import requests
import websockets
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from collections import deque

# Constants
INPUT_FILE = "/tmp/ftm_ip_list.txt"
OUTPUT_FILE = "/tmp/FTM250_nodes_with_blockNumber.csv"
FTM250_RPC_PORT = "8545"
FTM250_WS_PORT = "8546"
EXPECTED_CHAIN_ID = "0xfa"
MAX_CONCURRENT_WORKERS = 30
TIMEOUT = 1

HEADERS = {"content-type": "application/json"}
CHAIND_ID_PAYLOAD = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_chainId",
    "params": [],
}
BLOCK_NUMBER_PAYLOAD = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_blockNumber",
    "params": [],
}
PEERS_PAYLOAD = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "admin_peers",
    "params": [],
}

DISCOVERED_PEERS = set()
VISITED_PEERS = set()

rpc_open_ips = set()
ws_open_ips = set()


async def get_node_peers_ws(endpoint):
    chain_id = None
    command = f'timeout {TIMEOUT} wscat -x \'{{"jsonrpc":"2.0","method":"admin_peers","params":[],"id":1}}\' -c {endpoint}'
    result = await subprocess.run(command, shell=True, capture_output=True, text=True)

    try:
        result_json = json.loads(result.stdout)
        chain_id = result_json.get("result").lower()

    except Exception as e:
        return False

    return chain_id == EXPECTED_CHAIN_ID


async def check_ws_chain_id(endpoint):
    chain_id = None
    command = f'timeout {TIMEOUT} wscat -x \'{{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}}\' -c {endpoint}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    try:
        result_json = json.loads(result.stdout)
        chain_id = result_json.get("result").lower()

    except Exception as e:
        return False

    return chain_id == EXPECTED_CHAIN_ID


def check_rpc_available(url):
    try:
        response = requests.post(
            url, headers=HEADERS, json=CHAIND_ID_PAYLOAD, timeout=TIMEOUT
        )
        response_json = response.json()
        return response_json.get("result").lower() == EXPECTED_CHAIN_ID
    except Exception as e:
        return False


def get_block_number(url, is_ws):
    try:
        if is_ws:

            async def fetch_block_number():
                async with websockets.connect(url) as websocket:
                    await asyncio.wait_for(
                        websocket.send(json.dumps(BLOCK_NUMBER_PAYLOAD)),
                        timeout=TIMEOUT,
                    )
                    response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    response_json = json.loads(response)
                    return response_json.get("result")

            return asyncio.run(fetch_block_number())
        else:
            response = requests.post(
                url, headers=HEADERS, json=BLOCK_NUMBER_PAYLOAD, timeout=TIMEOUT
            )
            response_json = response.json()
            return response_json.get("result")
    except (asyncio.TimeoutError, websockets.exceptions.WebSocketException, Exception):
        return None


def get_node_peers_rpc(rpc_url):
    try:
        response = requests.post(
            rpc_url, headers=HEADERS, json=PEERS_PAYLOAD, timeout=TIMEOUT
        )
        response_json = response.json()
        peers = response_json.get("result", [])
        return [
            peer["network"]["remoteAddress"].split(":")[0]
            for peer in peers
            if "network" in peer and "remoteAddress" in peer["network"]
        ]
    except Exception as e:
        return []


def discover_peers_queue_rpc(initial_peers):
    queue = deque(initial_peers)

    while queue:
        current_peer = queue.popleft()
        if current_peer in VISITED_PEERS:
            continue
        VISITED_PEERS.add(current_peer)

        peers = get_node_peers_rpc(current_peer)
        for peer in peers:
            if "http" not in peer:
                peer_url = f"http://{peer}:{FTM250_RPC_PORT}"
            else:
                peer_url = peer
            if peer_url not in DISCOVERED_PEERS:
                DISCOVERED_PEERS.add(peer_url)
                queue.append(peer_url)


async def discover_peers_queue_ws(initial_peers):
    queue = deque(initial_peers)

    while queue:
        current_peer = queue.popleft()
        if current_peer in VISITED_PEERS:
            continue
        VISITED_PEERS.add(current_peer)

        peers = await get_node_peers_ws(current_peer)  # Use await for coroutine
        for peer in peers:
            peer_url = f"ws://{peer}:{FTM250_WS_PORT}"
            if peer_url not in DISCOVERED_PEERS:
                DISCOVERED_PEERS.add(peer_url)
                queue.append(peer_url)


def url_replace_to_port(ip, port):
    return f"http://{ip}:{port}"


def process_ip(ip):
    # adjust to cases where we already have RPCs from a list not only IPs
    if not "http" in ip or not "ws" in ip:
        url_rpc = url_replace_to_port(ip, FTM250_RPC_PORT)
        url_ws = url_replace_to_port(ip, FTM250_WS_PORT).replace("http", "ws")
    else:
        url_rpc = ip.replace("ws", "http")
        url_ws = ip.replace("http", "ws")

    if check_rpc_available(url_rpc):
        rpc_open_ips.add(url_rpc)

    if asyncio.run(check_ws_chain_id(url_ws)):
        ws_open_ips.add(url_ws)


def main():
    # Read the list of IPs from the input file
    with open(INPUT_FILE, "r") as file:
        ips = [line.strip() for line in file.readlines()]

    # Get all the IPs that have the expected chainId
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_WORKERS) as executor:
        futures = [executor.submit(process_ip, ip) for ip in ips]
        for _ in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Processing IPs - chainId verification",
        ):
            pass

    # Recursively discover peers using a queue
    initial_peers_rpc = list(rpc_open_ips)
    initial_peers_ws = list(ws_open_ips)
    discover_peers_queue_rpc(initial_peers_rpc)
    discover_peers_queue_ws(initial_peers_ws)

    # Collect block numbers for the saved IPs
    nodes_with_block_numbers = []

    for url in rpc_open_ips:
        block_number = get_block_number(url, is_ws=False)
        if block_number:
            nodes_with_block_numbers.append((url, "RPC", block_number))

    for url in ws_open_ips:
        block_number = get_block_number(url, is_ws=True)
        if block_number:
            nodes_with_block_numbers.append((url, "WS", block_number))

    # Save to CSV output file
    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        fieldnames = ["IP", "Type", "BlockNumber"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for node in nodes_with_block_numbers:
            writer.writerow({"IP": node[0], "Type": node[1], "BlockNumber": node[2]})


if __name__ == "__main__":
    main()
