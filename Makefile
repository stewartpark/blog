all: gen run

gen:
	python -m generator

run:
	python -m http.server --directory docs/ 8080

deploy:
	rm -rf docs/
	python -m generator
	git add -f docs/
	git commit -a -m "deploy"
	git push
