package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
)

type RequestPayload struct {
	Jsonrpc string        `json:"jsonrpc"`
	Method  string        `json:"method"`
	Params  []interface{} `json:"params"`
	ID      int           `json:"id"`
}

func main() {
	endpoints := []string{
		"http://x.x.x.x:8545",
		"https://linea-rpc.publicnode.com",
		"ws://127.0.0.1:8546",
		"wss://rpc.linea.build",
	}

	for _, endpoint := range endpoints {
		start := time.Now()
		if isWebSocket(endpoint) {
			testWebSocket(endpoint)
		} else {
			testHTTP(endpoint)
		}
		elapsed := time.Since(start).Seconds()
		fmt.Printf("Endpoint: %s, Time taken: %.2f seconds\n", endpoint, elapsed)
	}
}

func isWebSocket(endpoint string) bool {
	return len(endpoint) > 3 && endpoint[:2] == "ws"
}

func testHTTP(url string) {
	payload := RequestPayload{
		Jsonrpc: "2.0",
		Method:  "txpool_content",
		Params:  []interface{}{},
		ID:      1,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		fmt.Printf("Error creating JSON payload: %s\n", err)
		return
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("Error creating HTTP request: %s\n", err)
		return
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Error sending HTTP request: %s\n", err)
		return
	}
	defer resp.Body.Close()

	// Discard the response body to /dev/null
	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Error reading response body: %s\n", err)
		return
	}
}

func testWebSocket(url string) {
	c, _, err := websocket.DefaultDialer.Dial(url, nil)
	if err != nil {
		fmt.Printf("Error connecting to WebSocket: %s\n", err)
		return
	}
	defer c.Close()

	payload := RequestPayload{
		Jsonrpc: "2.0",
		Method:  "txpool_content",
		Params:  []interface{}{},
		ID:      1,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		fmt.Printf("Error creating JSON payload: %s\n", err)
		return
	}

	err = c.WriteMessage(websocket.TextMessage, jsonData)
	if err != nil {
		fmt.Printf("Error sending WebSocket message: %s\n", err)
		return
	}

	// Discard the response message to /dev/null
	_, _, err = c.ReadMessage()
	if err != nil {
		fmt.Printf("Error reading WebSocket response: %s\n", err)
		return
	}
}
