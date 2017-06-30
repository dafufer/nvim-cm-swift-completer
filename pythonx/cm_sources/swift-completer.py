# -*- coding: utf-8 -*-

# For debugging, use this command to start neovim:
#
# NVIM_PYTHON_LOG_FILE=nvim.log NVIM_PYTHON_LOG_LEVEL=INFO nvim
#
#
# Please register source before executing any other code, this allow cm_core to
# read basic information about the source without loading the whole module, and
# modules required by this module
from cm import register_source, getLogger, Base

register_source(name='swift-completer',
                priority=9,
                abbreviation='swift',
                scoping=True,
                scopes=['swift'],
                cm_refresh_patterns=[r'((?:\.|(?:,|:|->)\s+)\w*|\()'],)
                # cm_refresh_patterns=[r'(\.|:|:\s*\w*)$'],)


logger = getLogger(__name__)


class Source(Base):

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)

        # dependency check
        try:
            from distutils.spawn import find_executable
            if not find_executable("sourcekitten"):
                self.message('error', 'Can not find sourcekitten for completion, you need to install https://github.com/jpsim/SourceKitten')

            if not find_executable("swift") and self._check_xcode_path():
                self.message('error', 'Can not find swift or XCode: https://swift.org')

        except Exception as ex:
            logger.exception(ex)

        self.__spm = self.nvim.eval('swift_completer#get_spm_module()')
        self.__target = self.nvim.eval('swift_completer#get_target()')
        self.__sdk = self.nvim.eval('swift_completer#get_sdk()')


    def _check_xcode_path(self):
        from distutils.spawn import find_executable
        import subprocess

        if find_executable("xcode-select"):
            try:
                return subprocess.check_output(['xcode-select', '-p'])
            except subprocess.CalledProcessError as ex:
                logger.exception(ex)

        return None

    def cm_refresh(self, info, ctx, *args):
        import subprocess
        import json

        buf = self.nvim.current.buffer[:]
        lnum = ctx['lnum']
        startcol = ctx['startcol']
        col = startcol + 1
        enc = self.nvim.options['encoding']

        content = '\n'.join(buf)

        offset = 0
        for row_current, text in enumerate(buf):
            if row_current < lnum - 1:
                offset += len(bytes(text, enc)) + 1
                offset += col - 1

        try:
            # Set sourcekitten arguments
            args = ['sourcekitten', 'complete', '--text', content.encode(enc), '--offset', str(offset)]
            if self.__spm:
                args += ['--spm-module', self.__spm]

            if self.__target or self.__sdk:
                args += ['--']

            if self.__target:
                args += ['-target', self.__target]

            if self.__sdk:
                args += ['-sdk', self.__sdk]

            # Run sourcekitten command
            output, _ = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
            ).communicate()

            json_list = json.loads(output.decode())

        except subprocess.CalledProcessError:
            self.complete(info, ctx, startcol, [])
            return

        # logger.debug("args: %s, result: [%s]", args, output.decode())

        matches = []
        for item in json_list:
            name = item["sourcetext"]

            doc = ""
            if "docBrief" in item:
                doc = '\n' + item["docBrief"]
            des = item["descriptionKey"] + doc

            kind = item['kind'].split('.')[-1]
            if kind == "free":
                kind = item['kind'].split('.')[-2]

            snippet = item["sourcetext"]

            match = dict(word=name,
                         icase=1,
                         dup=1,
                         menu=kind,
                         info=des,
                         snippet=snippet,
                        )

            matches += match

        # logger.debug("matches: [%s]", matches)

        self.complete(info, ctx, startcol, matches)
