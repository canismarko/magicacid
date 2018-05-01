REMOTE=mwolf@simon.artiosonline.com:/srv/magicacid/
CONFIG=_config.yml,_config-deploy.yml
BUILD=jekyll build --config $(CONFIG)

all: css/magicacid.css
	$(BUILD)

css/magicacid.css: css/magicacid.less
	lessc --clean-css css/magicacid.less css/magicacid.css

deploy: all
	rsync -alvz --exclude 'bower_components' --del _site/ $(REMOTE)

serve:
	jekyll serve --watch --drafts --config _config.yml
