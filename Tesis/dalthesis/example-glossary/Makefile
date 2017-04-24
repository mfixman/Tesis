help:
	@echo make glossary - make glossary.pdf file with glossary
	@echo make glossary2 - make glossary.pdf file with glossary, via .dvi file

glossary:
	mkdir -p tmp
	cp glossary.tex glossary.sty simple.bib ../dalthesis.cls tmp/
	cd tmp; pdflatex glossary && bibtex glossary
	cd tmp;	makeindex -s glossary.ist -o glossary.gls glossary.glo
	cd tmp; pdflatex glossary
	cp tmp/glossary.pdf .

# A different way of producing pdf
glossary2:
	mkdir -p tmp
	cp glossary.tex glossary.sty simple.bib ../dalthesis.cls tmp/
	cd tmp; latex glossary && bibtex glossary
	cd tmp;	makeindex -s glossary.ist -o glossary.gls glossary.glo
	cd tmp; latex glossary
	cd tmp; dvipdf glossary.dvi glossary.pdf
	cp tmp/glossary.pdf .
