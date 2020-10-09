# get today's date (yyyy-mm-dd-hhmmss)
TODAY = $(shell date "+%Y-%m-%d-%H%M%S")

MODULES = "beautifulsoup4" "bs4" "mysql.connector" "pylint" "requests" "selenium"

create-venv:
	virtualenv -p /home/jacksonfossen/opt/python-3.8.1/bin/python3 venv

setup:
	# Create Output Directory
	if [[ ! -d "./output" ]] ; then \
		mkdir output ; \
	fi \

    #
	# Get Chrome Driver??

	# Install Packages
	@for lib in $(MODULES) ; do \
	  if pip3 list $$lib | grep -q "installed" ; then \
	    echo $$lib already installed, skipping ; \
	  else \
	    echo $$lib not found, installing... ; \
	    pip3 install $$lib ; \
	  fi \
	done;

clean:
	rm -rf output/*

super-clean: clean
	rm -rf past-output/*

save:
	# Creat Past-Output Directory
	if [[ ! -d "./past-output" ]] ; then \
		mkdir past-output ; \
	fi \

	# Competitions
	if [[ -a "./output/comp-table.txt"  ]] ; then \
		mv ./output/comp-table.txt ./past-output/comp-table-$(TODAY).txt ; \
	fi \

	# Events
	if [[ -a "./output/events.txt"  ]] ; then \
		mv ./output/events.txt ./past-output/events-$(TODAY).txt ; \
	fi \

	# Misfit Events
	if [[ -a "./output/misfit-events.txt"  ]] ; then \
		mv ./output/misfit-events.txt ./past-output/misfit-events-$(TODAY).txt ; \
	fi \

	# Placements
	if [[ -a "./output/placements.txt" ]] ; then \
		mv ./output/placements.txt ./past-output/placements-$(TODAY).txt ; \
	fi \

	# Misfit Placements
	if [[ -a "./output/misfit-placements.txt" ]] ; then \
		mv ./output/misfit-placements.txt ./past-output/misfit-placements-$(TODAY).txt ; \
	fi \

tables-recent: save
	python3 LevelUp.py recent

tables-all: save
	python3 LevelUp.py all