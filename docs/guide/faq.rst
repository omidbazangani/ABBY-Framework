Frequently Asked Questions
==========================

The PicoScope API crash during initialization
---------------------------------------------

Using a PicoScope 3207B, you might have to patch ``picoscope`` Python module to
make it works:

..  code-block:: diff

    diff --git a/picoscope/ps3000a.py b/picoscope/ps3000a.py
    index e24a172..59ae3f6 100644
    --- a/picoscope/ps3000a.py
    +++ b/picoscope/ps3000a.py
    @@ -205,11 +205,6 @@ class PS3000a(_PicoscopeBase):
                                            c_enum(VRange), c_float(VOffset))
            self.checkResult(m)

    -        m = self.lib.ps3000aSetBandwidthFilter(c_int16(self.handle),
    -                                               c_enum(chNum),
    -                                               c_enum(BWLimited))
    -        self.checkResult(m)
    -
        def _lowLevelStop(self):
            m = self.lib.ps3000aStop(c_int16(self.handle))
            self.checkResult(m)

This module is usually installed in ``~/.local/lib/python3``.
