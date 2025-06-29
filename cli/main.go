package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"time"
)

type Config struct {
	BaseURL string
	Token   string
}

func configPath() string {
	if runtime.GOOS == "windows" {
		return `C:\\DevTransClient\\config`
	}
	return "/opt/DevTransClient/config"
}

func loadConfig() Config {
	f, err := os.Open(configPath())
	if err != nil {
		return Config{}
	}
	defer f.Close()
	var cfg Config
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := strings.ToLower(strings.TrimSpace(parts[0]))
		val := strings.TrimSpace(parts[1])
		switch key {
		case "base_url":
			cfg.BaseURL = val
		case "token":
			cfg.Token = val
		}
	}
	return cfg
}

type UploadResp struct {
	Code   string `json:"code"`
	URL    string `json:"url"`
	Expiry string `json:"expiry"`
}

func formatExpiry(ts string) string {
	base := strings.Split(ts, ".")[0]
	t, err := time.ParseInLocation("2006-01-02T15:04:05", base, time.UTC)
	if err != nil {
		return ts
	}
	return t.Format("2006-01-02 15:04 MST")
}

func usage() {
	fmt.Println("Usage: devtrans <put|get> <path|code>")
	os.Exit(1)
}

func main() {
	if len(os.Args) < 3 {
		usage()
	}
	cfg := loadConfig()
	baseURL := os.Getenv("DEVTRANS_BASE_URL")
	if baseURL == "" {
		baseURL = cfg.BaseURL
	}
	if baseURL == "" {
		baseURL = "http://localhost:8000"
	}
	token := os.Getenv("DEVTRANS_TOKEN")
	if token == "" {
		token = cfg.Token
	}
	if token == "" {
		fmt.Println("missing API token: set DEVTRANS_TOKEN or edit", configPath())
		os.Exit(1)
	}

	switch os.Args[1] {
	case "put":
		path := os.Args[2]
		file, err := os.Open(path)
		if err != nil {
			fmt.Println("error opening file:", err)
			os.Exit(1)
		}
		defer file.Close()

		var buf bytes.Buffer
		writer := multipart.NewWriter(&buf)
		fw, err := writer.CreateFormFile("file", filepath.Base(path))
		if err != nil {
			fmt.Println("error creating form:", err)
			os.Exit(1)
		}
		if _, err := io.Copy(fw, file); err != nil {
			fmt.Println("error copying file:", err)
			os.Exit(1)
		}
		writer.Close()

		req, err := http.NewRequest("PUT", baseURL+"/upload", &buf)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		req.Header.Set("X-Filename", filepath.Base(path))

		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			fmt.Println("request error:", err)
			os.Exit(1)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			fmt.Println("upload failed:", resp.Status, string(body))
			os.Exit(1)
		}
		var r UploadResp
		json.NewDecoder(resp.Body).Decode(&r)

		exp := formatExpiry(r.Expiry)
		fmt.Println("=== DevTrans Upload ===")
		fmt.Printf(" Code:   %s\n", r.Code)
		fmt.Printf(" URL:    %s\n", r.URL)
		fmt.Printf(" Expires: %s\n", exp)
		fmt.Println("=======================")

	case "get":
		code := os.Args[2]
		resp, err := http.Get(baseURL + "/download/" + code)
		if err != nil {
			fmt.Println("request error:", err)
			os.Exit(1)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			fmt.Println("download failed:", resp.Status, string(body))
			os.Exit(1)
		}
		filename := resp.Header.Get("X-Filename")
		if filename == "" {
			filename = code
		}
		out, err := os.Create(filename)
		if err != nil {
			fmt.Println("error creating file:", err)
			os.Exit(1)
		}
		defer out.Close()
		io.Copy(out, resp.Body)
		fmt.Println("Saved", filename)
	default:
		usage()
	}
}
