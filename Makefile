.PHONY: cert

cert:
	@sh hack/make-cert.sh

clean:
	@rm -rf .bin .cert
