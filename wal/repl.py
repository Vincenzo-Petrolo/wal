'''Implementation of basic read-eval-print-loop'''
import cmd
from wal.core import Wal, wal_str
from wal.parsers import sexpr
from wal.ast import Operator
from . import __version__


class WalRepl(cmd.Cmd):
    '''WalRepl class implements basic read-eval-print-loop'''
    intro = f'WAL {__version__}\n'
    terminator = ['(', ')']
    wal = Wal()
    complete_list = [op.value for op in Operator]
    file = None

    @property
    def prompt(self):
        '''Generate prompt symbol'''
        traces = ', '.join(self.wal.traces.traces.keys())
        if self.wal.traces.traces:
            traces = traces + ' '
        return f'{traces}>-> '


    def onecmd(self, line):
        try:
            evaluated = self.wal.eval(line)
            if evaluated is not None:
                print(wal_str(evaluated))
        except Exception as e:  # pylint: disable=W0703,C0103
            print('ERROR|', e)
            print(line)

    def precmd(self, line):
        try:
            expr = sexpr.parse(line)
            # intercept defuns to include them in completion
            if isinstance(expr, list):
                if expr[0] == Operator.DEFUN:
                    self.complete_list.append(expr[1].name)

            return expr
        except Exception as e:  # pylint: disable=W0703,C0103
            print(e)
        return None

    def complete(self, text, state):
        return self.completenames(text)[state]

    def completenames(self, text, *ignored):
        tmp = self.complete_list + self.wal.traces.signals
        candidates = [c for c in tmp if c.startswith(text)]
        
#        if text[0] != '(' and len(candidates) == 1 and candidates[0] in self.complete_list:
#            candidates[0] = '(' + candidates[0] + ' '

        candidates.append(None)

        return candidates
