# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = documention
BUILDDIR      = build

TIKZPATH      = tikzimages
LATEX         = pdftex
OUTPUTDIR     = _static
TIKZBUILDDIR  = $(BUILDDIR)/$(TIKZPATH)

TIKZFILES	= $(wildcard $(SOURCEDIR)/$(TIKZPATH)/*.tex) 
DESIRED       = $(patsubst  $(SOURCEDIR)/$(TIKZPATH)/%.tex,$(SOURCEDIR)/$(OUTPUTDIR)/%.png, $(TIKZFILES))


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile tikz

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile tikz
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)



tikz: $(DESIRED)
	echo "Making all tikz images"

$(DESIRED): $(SOURCEDIR)/$(OUTPUTDIR)/%.png: $(SOURCEDIR)/$(TIKZPATH)/%.tex
	mkdir -p "$(TIKZBUILDDIR)"
	pdflatex -output-directory="$(TIKZBUILDDIR)" $^
	convert -density 300 \
	    	-size 1080x800 \
		-quality 90 \
	    "$(TIKZBUILDDIR)/$(patsubst $(SOURCEDIR)/$(TIKZPATH)/%.tex,%.pdf,$^)" $@
