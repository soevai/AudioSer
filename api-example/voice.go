package main

import (
	"bytes"
	"fmt"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
)

func main() {
	url := "http://127.0.0.1:5620/voice"
	file, err := os.Open("./1.wav")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close()
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile("file", "1.wav")
	if err != nil {
		fmt.Println(err)
		return
	}
	_, err = io.Copy(part, file)
	if err != nil {
		fmt.Println(err)
		return
	}
	writer.Close()
	request, err := http.NewRequest("POST", url, body)
	if err != nil {
		fmt.Println(err)
		return
	}
	request.Header.Set("Content-Type", writer.FormDataContentType())
	client := http.Client{}
	response, err := client.Do(request)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer response.Body.Close()
	responseBody, err := ioutil.ReadAll(response.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(responseBody))
}
