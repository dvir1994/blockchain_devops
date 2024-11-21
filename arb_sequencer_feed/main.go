// Arbitrum sequencer feed watcher
// https://www.degencode.com/p/decoding-the-arbitrum-sequencer-feed
package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/gorilla/websocket"
)

const sequencerURI = "wss://arb1.arbitrum.io/feed"

type sequencerPayload struct {
	Messages []struct {
		Message struct {
			Message struct {
				Header struct {
					Kind int `json:"kind"`
				} `json:"header"`
				L2Msg string `json:"l2Msg"`
			} `json:"message"`
		} `json:"message"`
	} `json:"messages"`
}

func watchSequencerFeed() {
	fmt.Println("Starting sequencer feed watcher")

	for {
		c, _, err := websocket.DefaultDialer.Dial(sequencerURI, nil)
		if err != nil {
			log.Printf("WebSocket connection error: %v", err)
			continue
		}
		defer c.Close()

		for {
			_, message, err := c.ReadMessage()
			if err != nil {
				log.Printf("Read error: %v", err)
				break
			}

			var payload sequencerPayload
			err = json.Unmarshal(message, &payload)
			if err != nil {
				log.Printf("JSON unmarshal error: %v", err)
				continue
			}

			for _, msg := range payload.Messages {

				// Kind 3 is a transaction
				if msg.Message.Message.Header.Kind != 3 {
					continue
				}

				rawTx, err := base64.StdEncoding.DecodeString(msg.Message.Message.L2Msg)
				if err != nil {
					log.Printf("Base64 decode error: %v", err)
					continue
				}

				if rawTx[0] != 4 {
					continue
				}

				var tx types.Transaction

				err = tx.UnmarshalBinary(rawTx[1:])
				if err != nil {
					log.Printf("UnmarshalBinary error: %v", err)
					continue
				}

				txHash := common.BytesToHash(rawTx[2:]).Hex()
				fmt.Printf("Type: %d,	Hash: %s\n", tx.Type(), txHash)

			}
		}
	}
}

func main() {
	watchSequencerFeed()
	fmt.Println("Complete")
}
