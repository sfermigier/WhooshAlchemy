.PHONY: test clean

test:
	nosetests

clean:
	rm -rf *.pyc
	rm -rf *.egg-info
