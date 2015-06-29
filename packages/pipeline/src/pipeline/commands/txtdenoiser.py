"""Package to clean TXT files

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
import codecs
from os.path import join, isfile, splitext, basename
from os import listdir
from denoiser import Denoiser
from pipeline.command import Command


class TXTDenoiser(Command):
    """Command to clean TXT files
    """

    def __init__(self, filename, logger, config):
        super(TXTDenoiser, self).__init__(filename, logger, config)
        self.denoiser = Denoiser(config)

    def execute(self):
        try:
            self.logger.debug("::: Text cleaning :::")
            super(TXTDenoiser, self).get_file()

            txt_dir = join(self.unzipped, "txt")
            txt_files = [join(txt_dir, f) for f in listdir(txt_dir) if isfile(join(txt_dir, f)) and f.endswith(".txt")]

            if len(txt_files) != 1:
                self.logger.error("Incorrect number of text files")
                self.finalize()
                return -1

            text_data = self.denoiser.cleanse(txt_files[0], False)

            # Writing classified lines
            base_filename = splitext(basename(txt_files[0]))[0]
            clean_filename = join(txt_dir, base_filename+".clean.txt")
            garbage_filename = join(txt_dir, base_filename+".grbge.txt")
            unclassified_filename = join(txt_dir, base_filename+".unclss.txt")

            with codecs.open(clean_filename, "wb", encoding="utf-8") as clean_file:
                for line in text_data.get_clean_lines():
                    clean_file.write(line+"\n")

            with codecs.open(garbage_filename, "wb", encoding="utf-8") as garbage_file:
                for line in text_data.get_garbage_lines():
                    garbage_file.write(line+"\n")

            if len(text_data.get_unclassified_lines()) > 0:
                with codecs.open(unclassified_filename, "wb", encoding="utf-8") as unclassified_file:
                    for line in text_data.get_unclassified_lines():
                        unclassified_file.write(line+"\n")
        except Exception, e:
            print e

            self.logger.error("Cleaner has stopped unexpectedly: "+e.message)
            self.finalize()
            return -2

        self.finalize()
        return 0

    def finalize(self):
        super(TXTDenoiser, self).store_file()
        self.logger.debug("::: Text cleaning (END) :::")
