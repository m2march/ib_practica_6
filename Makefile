.PHONY: show_comp all

all: show_comp

show_comp: comp.txt
	cat $<

comp.txt: comp_py_wppl.py ejercicio.wppl.json ejercicio.py.json
	python $^

ejercicio.wppl.json: ejercicio.wppl
	webppl $< > $@

ejercicio.py.json: ejercicio.py ib.py
	python $< > $@

clean:
	rm -f ejercicio.wppl.json
	rm -f ejercicio.py.json
	rm -f comp.txt
