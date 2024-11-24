// Package main provides tools to fetch and test the content of transaction pools from various blockchain endpoints.
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

// RequestPayload represents the payload for JSON-RPC requests.
type RequestPayload struct {
	Jsonrpc string        `json:"jsonrpc"`
	Method  string        `json:"method"`
	Params  []interface{} `json:"params"`
	ID      int           `json:"id"`
}

// EndpointResult represents the result of testing an endpoint for mempool support.
type EndpointResult struct {
	endpoint   string
	supported  bool
	timeTaken  float64
	resultSize int
}

func main() {
	// Use a map to ensure unique endpoints
	endpointSet := make(map[string]struct{})

	// Add endpoints to the set
	endpoints := []string{
		"ws://x.x.x.x:8546",
		"https://1rpc.io/celo",
		"http://x.x.x.x:8545",
	}

	// Add to set to ensure uniqueness
	for _, endpoint := range endpoints {
		endpointSet[endpoint] = struct{}{}
	}

	var wg sync.WaitGroup
	results := make(chan EndpointResult, len(endpointSet))

	// Process unique endpoints
	for endpoint := range endpointSet {
		wg.Add(1)
		go func(endpoint string) {
			defer wg.Done()

			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()

			start := time.Now()
			var result EndpointResult
			result.endpoint = endpoint

			if isWebSocket(endpoint) {
				result.supported, result.resultSize = testWebSocket(ctx, endpoint)
			} else {
				result.supported, result.resultSize = testHTTP(ctx, endpoint)
			}

			result.timeTaken = time.Since(start).Seconds()
			if result.supported {
				results <- result
			}
		}(endpoint)
	}

	// Close channel after all goroutines complete
	go func() {
		wg.Wait()
		close(results)
	}()

	// Print results as they come in
	fmt.Printf("Testing %d unique endpoints for mempool support:\n\n", len(endpointSet))
	for result := range results {
		fmt.Printf("- %s\n  Time taken: %.2f seconds\n  Result size: %d characters\n\n",
			result.endpoint,
			result.timeTaken,
			result.resultSize,
		)
	}
}

func isWebSocket(endpoint string) bool {
	return strings.HasPrefix(endpoint, "ws")
}

func testHTTP(ctx context.Context, url string) (bool, int) {
	payload := RequestPayload{
		Jsonrpc: "2.0",
		Method:  "txpool_content",
		Params:  []interface{}{},
		ID:      1,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return false, 0
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return false, 0
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return false, 0
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return false, 0
	}

	var response map[string]interface{}
	if err := json.Unmarshal(body, &response); err != nil {
		return false, 0
	}

	result, exists := response["result"]
	if !exists {
		return false, 0
	}

	// Convert result back to JSON to count its characters
	resultJSON, err := json.Marshal(result)
	if err != nil {
		return true, 0 // Still return true as mempool is supported, but size is unknown
	}

	return true, len(string(resultJSON))
}

func testWebSocket(ctx context.Context, url string) (bool, int) {
	dialer := websocket.Dialer{
		HandshakeTimeout: 5 * time.Second,
	}

	c, _, err := dialer.DialContext(ctx, url, nil)
	if err != nil {
		return false, 0
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
		return false, 0
	}

	err = c.WriteMessage(websocket.TextMessage, jsonData)
	if err != nil {
		return false, 0
	}

	resultChan := make(chan struct {
		supported bool
		size      int
	})

	go func() {
		_, message, err := c.ReadMessage()
		if err != nil {
			resultChan <- struct {
				supported bool
				size      int
			}{false, 0}
			return
		}

		var response map[string]interface{}
		if err := json.Unmarshal(message, &response); err != nil {
			resultChan <- struct {
				supported bool
				size      int
			}{false, 0}
			return
		}

		result, exists := response["result"]
		if !exists {
			resultChan <- struct {
				supported bool
				size      int
			}{false, 0}
			return
		}

		// Convert result back to JSON to count its characters
		resultJSON, err := json.Marshal(result)
		if err != nil {
			resultChan <- struct {
				supported bool
				size      int
			}{true, 0} // Still return true as mempool is supported, but size is unknown
			return
		}

		resultChan <- struct {
			supported bool
			size      int
		}{true, len(string(resultJSON))}
	}()

	select {
	case <-ctx.Done():
		return false, 0
	case result := <-resultChan:
		return result.supported, result.size
	}
}
