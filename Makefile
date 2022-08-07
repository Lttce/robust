.PHONY: all
all:

.PHONY: send
send:
	python3 main.py c 127.0.0.1 8000

.PHONY: receive
receive:
	python3 main.py s 127.0.0.1 8000

.PHONY: check
check:
	python3 cmp.py
	
.PHONY: ready
ready:
	./data/ready.sh
