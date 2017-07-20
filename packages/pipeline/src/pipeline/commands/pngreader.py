"""Package to convert PNG to TXT

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
from os.path import join, isdir, split, dirname, basename, splitext, isfile
from subprocess import check_output, STDOUT
from os import listdir
from shutil import move
from pipeline.command import Command


class PNGReader(Command):
    """Command to convert PNG to TXT
    """

    def __init__(self, filename, logger, config):
        super(PNGReader, self).__init__(filename, logger, config)

        self.proc_count = 1
        self.ocropus_dir = self.config["command"]["ocropy"]["location"]
        self.rpred_model = self.config["command"]["ocropy"]["model"]
        self.python = ["python"]

        self.logger.info("PNG reader initialized")

    def execute(self):
        """Execute the command
        """
        self.logger.debug("::: PNG reading :::")
        # super(PNGReader, self).get_file()

        procs = str(self.proc_count)

        png_dir = join(self.unzipped, "png")
        txt_dir = join(self.unzipped, "txt")

        command_list = [
            [join(self.ocropus_dir, 'ocropus-nlbin'), "-Q", procs, join(png_dir, '*.png')],
            [join(self.ocropus_dir, 'ocropus-gpageseg'), "-Q", procs, join(png_dir, '*.bin.png')],
            [join(self.ocropus_dir, 'ocropus-rpred'), "-Q", procs, "-m", self.rpred_model,
             join(png_dir, '*/*.bin.png')],
        ]

        # Execute the list of command
        for command in command_list:
            try:
                self.logger.debug("> "+str(command))

                cmdout = check_output(self.python+command, stderr=STDOUT)
                self.logger.info(cmdout)
            except Exception, e:
                print e
                self.logger.fatal("An exception has been caugth: "+str(e.message))
                self.finalize()
                return 1

        # Build the resulting text file from every line file
        txt_files = [join(png_dir, subdir, f) for subdir in listdir(png_dir) if isdir(join(png_dir, subdir))
                     for f in listdir(join(png_dir, subdir)) if f.endswith(".txt")]
        self.logger.debug(str(len(txt_files)) + " text file(s) found")

        for f in txt_files:
            dirs = split(dirname(f))

            filename = basename(f)
            pagenum = dirs[-1].split("-")[-1]

            move(f, join(txt_dir, "segments", pagenum+"-"+filename))

        txt_files = sorted([join(txt_dir, "segments", f) for f in listdir(join(txt_dir, "segments"))
                            if f.endswith(".txt")])

        text = ""
        for f in txt_files:
            with open(f, "r") as txt:
                lines = txt.readlines()

                for l in lines:
                    text += l

        pdf_files = [join(self.unzipped, f) for f in listdir(self.unzipped) if isfile(join(self.unzipped, f)) and
                     f.endswith(".pdf")]
        txt_filename = splitext(basename(pdf_files[0]))[0]+".txt"

        with open(join(txt_dir, txt_filename), "w") as output:
            output.write(text)

        self.finalize()
        return 0

    def finalize(self):
        """Finalize the job
        """
        # super(PNGReader, self).store_file()
        self.logger.debug("::: PNG reading (END) :::")
