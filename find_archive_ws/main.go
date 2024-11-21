// Package Main checks if there is any archive node out of all the endpoints
package main

import (
	"fmt"
	"log"
	"sync"

	"github.com/gorilla/websocket"
)

func sendRequest(endpoint string, wg *sync.WaitGroup) {
	defer wg.Done()

	// Dial the WebSocket connection
	conn, _, err := websocket.DefaultDialer.Dial(endpoint, nil)
	if err != nil {
		log.Printf("Error connecting to %s: %v\n", endpoint, err)
		return
	}
	defer conn.Close()

	// JSON-RPC message
	message := `{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xd8da6bf26964af9d7eed9e03e53415d37aa96045", "0x10"],"id":1}`

	// Send the message
	err = conn.WriteMessage(websocket.TextMessage, []byte(message))
	if err != nil {
		log.Printf("Error sending message to %s: %v\n", endpoint, err)
		return
	}

	// Read the response
	_, response, err := conn.ReadMessage()
	if err != nil {
		log.Printf("Error reading response from %s: %v\n", endpoint, err)
		return
	}

	// Print the response
	fmt.Printf("Response from %s: %s\n", endpoint, string(response))
}

func main() {
	// List of endpoints
	endpoints := []string{
		"ws://x.x.x.x:9650/ext/bc/C/ws",
		"ws://y.y.y.y:9650/ext/bc/C/ws",
	}

	// WaitGroup to wait for all goroutines to finish
	var wg sync.WaitGroup

	// Loop over each endpoint and send the request in parallel
	for _, endpoint := range endpoints {
		wg.Add(1)
		go sendRequest(endpoint, &wg)
	}

	// Wait for all goroutines to finish
	wg.Wait()
}
