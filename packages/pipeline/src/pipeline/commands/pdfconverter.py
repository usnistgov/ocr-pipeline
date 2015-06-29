"""Package to convert PDF to PNG

.. Authors:
    Philippe Dessauw
    philippe.dessauw@nist.gov

.. Sponsor:
    Alden Dima
    alden.dima@nist.gov
    Information Systems Group
    Software and Systems Division
    Information Technology Laboratory
    National Institute of Standards and Technology
    http://www.nist.gov/itl/ssd/is
"""
from os import listdir
from os.path import join, isfile, dirname, splitext, basename
import PyPDF2
import PythonMagick
from pipeline.command import Command


class PDFConverter(Command):
    """Command to convert PDF to PNG.
    """

    def __init__(self, filename, logger, config):
        super(PDFConverter, self).__init__(filename, logger, config)

        self.density = config["command"]["density"]
        self.depth = config["command"]["depth"]
        self.quality = config["command"]["quality"]

        self.logger.debug("PDF converter {density: "+str(self.density)
                          + "; depth: "+str(self.depth)
                          + "; quality: "+str(self.quality) + "}")

    def execute(self):
        self.logger.debug(":::    PDF conversion    :::")
        super(PDFConverter, self).get_file()

        self.logger.debug(str(listdir(self.unzipped)))
        pdf_list = [join(self.unzipped, f) for f in listdir(self.unzipped)
                    if isfile(join(self.unzipped, f)) and f.endswith(".pdf")]

        if len(pdf_list) != 1:
            self.logger.error("Incorrect number of PDF file in " + self.unzipped
                              + " (" + str(len(pdf_list)) + " found, 1 expected)")
            self.finalize()
            return 1

        filename = str(pdf_list[0])
        with open(filename, "rb") as pdf:
            pdf_filereader = PyPDF2.PdfFileReader(pdf)
            pdf_page_nb = pdf_filereader.getNumPages()

        pdf_dirname = dirname(filename)
        imagesdir = "png"

        self.logger.debug(str(pdf_page_nb) + " page(s) detected")
        for p in xrange(pdf_page_nb):

            try:  # Reading the PDF
                img = PythonMagick.Image()
                img.density(str(self.density))
                img.depth(self.depth)
                img.quality(self.quality)

                pdf_page_file = filename + '[' + str(p) + ']'
                self.logger.debug("Reading " + pdf_page_file + "...")
                img.read(pdf_page_file)

                png_dirname = join(pdf_dirname, imagesdir)
                png_filename = splitext(basename(filename))[0] + '-' + str(p) + '.png'
                png_page_file = join(png_dirname, png_filename)
                self.logger.debug("Writing " + png_page_file + "...")
                img.write(png_page_file)
            except Exception, e:
                self.logger.fatal("An exception has been caugth: "+str(e.message))
                self.finalize()
                return 1

        self.finalize()
        return 0

    def finalize(self):
        super(PDFConverter, self).store_file()
        self.logger.debug("::: PDF conversion (END) :::")
