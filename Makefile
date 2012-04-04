.PHONY: test doctest clean

test:
	nosetests

doctest:
	nosetests --with-doctest --doctest-extension=rst

clean:
	rm -rf *.pyc
	rm -rf *.egg-info
	rm -rf build dist
