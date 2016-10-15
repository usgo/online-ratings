package main

import (
	"io"
	"log"
	"net/http"
)

func hello(w http.ResponseWriter, r *http.Request) {
	log.Printf("Req.URL: %v, Req.Method: %v", r.URL, r.Method)
	io.WriteString(w, "Hello world!")
}

func main() {
	http.HandleFunc("/", hello)
	http.ListenAndServe(":3000", nil)
}
