// ****************************************************************************************************************
// this code include ONLY the modification needed for Gatus to support RPC latest block height comparison
// this functionality is used in order to track that internal nodes in our network are synced
// original file to be modified - https://github.com/TwiN/gatus/blob/master/config/endpoint/condition.go
// ****************************************************************************************************************

package core

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
)

const (

	//
	// For block number comparison
	BlockNumFunctionPrefix = "blockNum("
)

func decodeHex(hex interface{}) (int64, error) {
	hexStr := fmt.Sprintf("%v", hex)
	value, err := strconv.ParseInt(hexStr, 0, 64)
	if err != nil {
		return 0, err
	}
	return value, nil
}

func ethBlockNum(result *Result, compareRpcs []string, first string) (int64, int64, bool) {
	var firstI, secondI int64

	firstI, err := strconv.ParseInt(first, 0, 64)
	if err != nil {
		result.AddError("Error parsing input: " + err.Error())
		return 0, 0, false
	}

	for _, compareRpc := range compareRpcs {
		resp, err := http.Post(
			compareRpc,
			"application/json",
			bytes.NewBuffer([]byte(`{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}`)),
		)
		if err != nil {
			continue
		}

		var res map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&res)
		if err != nil {
			continue
		}

		secondI, err = decodeHex(res["result"])
		if err != nil {
			continue
		}
	}
	if secondI == 0 {
		result.AddError("error grabbing block from external rpc")
		return 0, 0, false
	}

	return firstI, secondI, true
}

func blockNum(result *Result, first, second string) bool {
	//
	// Skip evaluation on init (or else it breaks)
	if strings.Contains(first, InvalidConditionElementSuffix) {
		return false
	}

	args := strings.Split(second, ",")
	if len(args) < 3 {
		result.AddError("Bad configuration! " + second)
		return false
	}
	deltaThreshold, err := strconv.ParseInt(args[0], 10, 64)
	if err != nil {
		result.AddError(err.Error())
		return false
	}
	var firstI, secondI int64
	chainType := args[1]

	compareRpc := args[2:]

	switch chainType {
	case "eth":
		var isOk bool
		firstI, secondI, isOk = ethBlockNum(result, compareRpc, first)
		if !isOk {
			return isOk
		}

	}
	result.AddError(fmt.Sprintf("rpc: %d, reference: %d, diff: %d", firstI, secondI, secondI-firstI))
	return !(absInt(secondI-firstI) > deltaThreshold)
}

func absInt(number int64) int64 {
	if number < 0 {
		return -number
	} else {
		return number
	}
}
