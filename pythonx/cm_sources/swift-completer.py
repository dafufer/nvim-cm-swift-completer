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
                cm_refresh_patterns=[r'(\.|:|: )$'],)

import json
import os
import subprocess
import glob


logger = getLogger(__name__)


class Source(Base):

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)

        # dependency check
        try:
            from distutils.spawn import find_executable
            if not find_executable("sourcekitten"):
                self.message('error', 'Can not find sourcekitten for completion, you need https://github.com/jpsim/SourceKitten' )
            if not find_executable("swift") and _check_xcode__path:
                self.message('error', 'Can not find swift or XCode: https://swift.org' )
        except Exception as ex:
            logger.exception(ex)

    def _check_xcode_path(self):
        if find_executable("xcode-select"):
            return subprocess.check_output(['xcode-select', '-print-path'])

        return None

    def cm_refresh(self, info, ctx, *args):
        src = self.get_src(ctx).encode('utf-8')
        lnum = ctx['lnum']
        col = ctx['col']
        filepath = ctx['filepath']
        startcol = ctx['startcol']


        offset = 0
        for current_line, text in enumerate(src.splitlines()):
            if current_line < lnum - 1:
                offset += len(text) + 1
            elif current_line == lnum - 1:
                offset += len(text[0:col]) - 1
                break

        # This is a hack to show init methods correctly
        if src[offset] in b'. :':
            offset += 1

        args = ['sourcekitten', 'complete', '--text', src, '--offset', str(offset)]
        result = subprocess.check_output(args)
        # proc = subprocess.Popen(args=args,
                                # stdin=subprocess.PIPE,
                                # stdout=subprocess.PIPE,
                                # stderr=subprocess.PIPE)

        # try:
            # result, errs = proc.communicate(src, timeout=30)
        # except TimeoutExpired:
            # proc.kill()
            # result, errs = proc.communicate()

        logger.info("args: %s, result: [%s]", args, result.decode())

        matches = []
        jsonList = json.loads(result.decode('utf-8'))
        for item in jsonList:
            name = item["name"].replace(":", "")
            des = item["descriptionKey"]
            doc = ""
            if "docBrief" in item:
                doc = item["docBrief"]
            snippet = item["sourcetext"]
            match = dict(word=name,
                        icase=1,
                        dup=1,
                        menu=des,
                        snippet=snippet,
                        )

            matches.append(match)

        # logger.info("matches: [%s]", matches)

        self.complete(info, ctx, startcol, matches)
