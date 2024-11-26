// Package main provides a simple Prometheus exporter for the Gaia blockchain node.
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// URL of the Gaia node status endpoint
const statusURL = "http://localhost:26657/status"

var (
	blockHeight = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "gaia_block_height",
		Help: "Current block height",
	})
	blockTimeDrift = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "gaia_block_time_drift_seconds",
		Help: "Current block time drift in seconds",
	})
	peersCount = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "gaia_peers_count",
		Help: "Amount of connected peers",
	})
	peersByVersion = prometheus.NewGaugeVec(prometheus.GaugeOpts{
		Name: "gaia_version_by_peers",
		Help: "Amount of peers by version",
	}, []string{"version"})
)

func init() {
	prometheus.MustRegister(blockHeight)
	prometheus.MustRegister(blockTimeDrift)
	prometheus.MustRegister(peersCount)
	prometheus.MustRegister(peersByVersion)
}

type statusResponse struct {
	Result struct {
		SyncInfo struct {
			LatestBlockHeight string    `json:"latest_block_height"`
			LatestBlockTime   time.Time `json:"latest_block_time"`
		} `json:"sync_info"`
	} `json:"result"`
}

type netInfoResponse struct {
	Result struct {
		Peers []struct {
			NodeInfo struct {
				Version string `json:"version"`
			} `json:"node_info"`
		} `json:"peers"`
	} `json:"result"`
}

func updateMetrics() {
	statusResp, err := http.Get(statusURL)
	if err == nil {
		defer statusResp.Body.Close()
		body, _ := io.ReadAll(statusResp.Body)
		var status statusResponse
		json.Unmarshal(body, &status)

		height, _ := strconv.ParseInt(status.Result.SyncInfo.LatestBlockHeight, 10, 64)
		blockHeight.Set(float64(height))

		drift := time.Now().Sub(status.Result.SyncInfo.LatestBlockTime).Seconds()
		blockTimeDrift.Set(drift)
	}

	netInfoResp, err := http.Get("http://localhost:26657/net_info")
	if err == nil {
		defer netInfoResp.Body.Close()
		var netInfo netInfoResponse
		json.NewDecoder(netInfoResp.Body).Decode(&netInfo)

		peersCount.Set(float64(len(netInfo.Result.Peers)))

		versionCount := make(map[string]int)
		for _, peer := range netInfo.Result.Peers {
			versionCount[peer.NodeInfo.Version]++
		}
		for version, count := range versionCount {
			peersByVersion.WithLabelValues(version).Set(float64(count))
		}
	}
}

func main() {
	go func() {
		for {
			updateMetrics()
			time.Sleep(15 * time.Second)
		}
	}()

	http.Handle("/metrics", promhttp.Handler())
	fmt.Println("Exporter is running on :9100")
	http.ListenAndServe(":9100", nil)
}
