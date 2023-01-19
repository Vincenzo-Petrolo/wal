'''Trace implementation for the FST file format '''

import re
import pylibfst as fst

from wal.trace.trace import Trace

class TraceFst(Trace):
    '''Holds data for one fst trace.'''

    def __init__(self, file, tid, from_string=False):
        self.tid = tid
        self.buf = fst.ffi.new("char[256]")

        if from_string:
            raise ValueError("FST traces do not support the from_string argument")

        self.fst = fst.lib.fstReaderOpen(file.encode('utf-8'))
        self.filename = file

        # get scopes and signals
        (self.scopes, signals) = fst.get_scopes_signals2(self.fst)
        self.references_to_ids = signals.by_name

        # get mapping from name to tid and remove trailing signal width, ' [31:0]' etc.
        self.references_to_ids = {re.sub(r' *\[\d+:\d+\]', '', k): v for
                                        k, v in self.references_to_ids.items()}
        # rename grouped signals like reg(0), reg(1) to reg_0, reg_1
        self.references_to_ids = {
            re.sub(r'\(([0-9]+)\)', r'_\1', k): v for k, v in self.references_to_ids.items()}

        self.rawsignals = list(self.references_to_ids.keys())
        self.signals = set(Trace.SPECIAL_SIGNALS + self.rawsignals)

        # remove duplicate timestamps, enumerate all timestamps and create look up table
        fst.lib.fstReaderSetFacProcessMaskAll(self.fst)
        raw_timestamps = fst.lib.fstReaderGetTimestamps(self.fst)
        self.all_timestamps = raw_timestamps.val
        self.timestamps = self.all_timestamps

        # stores current time stamp
        self.index = 0
        self.max_index = raw_timestamps.nvals - 1

    def access_signal_data(self, name, index):
        '''Backend specific function for accessing signals in the waveform'''
        handle = self.references_to_ids[name].handle
        return fst.helpers.string(fst.lib.fstReaderGetValueFromHandleAtTime(self.fst, self.timestamps[index], handle, self.buf))

    def signal_width(self, name):
        return self.references_to_ids[name].length
