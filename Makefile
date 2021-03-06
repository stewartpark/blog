all: gen run

gen:
	python -m generator

run:
	python -m http.server --directory docs/ 8080

dev:
	TMUX= tmux \
		  new-session 'while true; do make gen; sleep 1; done' \; \
		  split-window 'python -m http.server --directory docs/ 8080' \; \
		  split-window 'jupyter notebook'

deploy:
	rm -rf docs/*.html docs/{assets,notebooks,tags}
	python -m generator
	git add -f docs/
	git commit -a -m "deploy"
	git push
